package com.example.android_app

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.os.Environment
import android.provider.MediaStore
import android.util.Log
import android.widget.Button
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import android.widget.LinearLayout
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import com.example.android_app.utils.DataParser
import okhttp3.Call
import okhttp3.Callback
import okhttp3.MediaType
import okhttp3.MultipartBody
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody
import okhttp3.Response
import java.io.File
import java.io.IOException

class MainActivity : AppCompatActivity() {
    private lateinit var photoUri: Uri

    private val takePictureLauncher = registerForActivityResult(
        ActivityResultContracts.TakePicture()
    ) { success ->
        if (success) {
            // Now send the image to the server
            uploadImageToServer(photoUri)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_main)

        // 🔒 PROTECȚIE: dacă NU e logat → Login
        val token = getSharedPreferences("auth", MODE_PRIVATE)
            .getString("token", null)

        if (token == null) {
            startActivity(Intent(this, LoginActivity::class.java))
            finish()
            return
        }

        val rootLayout = findViewById<LinearLayout>(R.id.main)
        ViewCompat.setOnApplyWindowInsetsListener(rootLayout) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
        }

        val scanButton = findViewById<Button>(R.id.scan_button)
        val statsButton = findViewById<Button>(R.id.stats_button)
        val logoutButton = findViewById<Button>(R.id.btnLogout)   // 🔴 NOU

        scanButton.setOnClickListener {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
                != PackageManager.PERMISSION_GRANTED
            ) {
                ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.CAMERA), 100)
            } else {
                val photoFile = createImageFile()
                photoUri = FileProvider.getUriForFile(
                    this,
                    "${packageName}.fileprovider",
                    photoFile
                )
                takePictureLauncher.launch(photoUri)
            }
        }

        statsButton.setOnClickListener {
            val intent = Intent(this, StatisticsActivity::class.java)
            startActivity(intent)
        }

        // 🔴 LOGOUT
        logoutButton.setOnClickListener {
            doLogout()
        }
    }
    private fun doLogout() {
        getSharedPreferences("auth", MODE_PRIVATE)
            .edit()
            .remove("token")
            .apply()

        val intent = Intent(this, LoginActivity::class.java)
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        startActivity(intent)
    }


    override fun onRequestPermissionsResult(
        requestCode: Int, permissions: Array<out String>, grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)

        if (requestCode == 100 &&
            grantResults.isNotEmpty() &&
            grantResults[0] == PackageManager.PERMISSION_GRANTED
        ) {
            openCamera()
        }
    }

    private fun openCamera() {
        val intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
        startActivity(intent)
    }

    private fun createImageFile(): File {
        val storageDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES)
        return File.createTempFile(
            "receipt_", ".jpg",
            storageDir
        )
    }

    private fun uploadImageToServer(imageUri: Uri) {
        // Get the authentication token
        val token = getSharedPreferences("auth", MODE_PRIVATE).getString("token", null)

        if (token == null) {
            Log.e("API", "No authentication token found")
            runOnUiThread {
                android.widget.Toast.makeText(this, "Please login first", android.widget.Toast.LENGTH_SHORT).show()
            }
            return
        }

        val contentResolver = contentResolver
        val inputStream = contentResolver.openInputStream(imageUri)
        val imageBytes = inputStream?.readBytes() ?: return

        val requestFile = RequestBody.create(
            MediaType.parse("image/jpeg"),
            imageBytes
        )

        val body = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart(
                "file",
                "receipt.jpg",
                requestFile
            )
            .build()

        val request = Request.Builder()
            .url("${RetrofitInstance.baseUrl}extract")
            .addHeader("Authorization", "Bearer $token")  // Add JWT token
            .post(body)
            .build()

        val client = OkHttpClient()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                Log.e("API", "Network failure: $e")
                runOnUiThread {
                    android.widget.Toast.makeText(
                        this@MainActivity,
                        "Network error: ${e.message}",
                        android.widget.Toast.LENGTH_LONG
                    ).show()
                }
            }

            override fun onResponse(call: Call, response: Response) {
                // 1. Get the raw JSON string
                val responseData = response.body()?.string()

                if (response.isSuccessful && responseData != null) {
                    try {
                        // 2. Parse the JSON using the method we wrote
                        val extraction = DataParser.extractData(responseData)

                        // Log the results for debugging
                        Log.d("API", "Extracted ${extraction.items.size} items.")
                        Log.d("API", "Total Price: ${extraction.totalPrice}")
                        Log.d("API", "Response data: $responseData")

                        // 3. Show success message
                        runOnUiThread {
                            android.widget.Toast.makeText(
                                this@MainActivity,
                                "Receipt processed! Total: ${extraction.totalPrice}",
                                android.widget.Toast.LENGTH_LONG
                            ).show()
                        }

                    } catch (e: Exception) {
                        Log.e("API", "Parsing error: ${e.message}")
                        runOnUiThread {
                            android.widget.Toast.makeText(
                                this@MainActivity,
                                "Error parsing receipt data",
                                android.widget.Toast.LENGTH_SHORT
                            ).show()
                        }
                    }
                } else {
                    val errorMsg = when (response.code()) {
                        401 -> "Authentication failed. Please login again."
                        400 -> "Invalid receipt image"
                        500 -> "Server error. Please try again."
                        503 -> "Model not loaded on server"
                        else -> "Server Error: ${response.code()}"
                    }
                    Log.e("API", "Server Error: ${response.code()} - ${response.message()}")
                    Log.e("API", "Response body: $responseData")

                    runOnUiThread {
                        android.widget.Toast.makeText(
                            this@MainActivity,
                            errorMsg,
                            android.widget.Toast.LENGTH_LONG
                        ).show()

                        // If 401, redirect to login
                        if (response.code() == 401) {
                            doLogout()
                        }
                    }
                }
            }
        })
    }


}
