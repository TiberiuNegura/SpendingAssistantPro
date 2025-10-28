package com.example.android_app

import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_main)

        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
        }


        val buttonPing = findViewById<Button>(R.id.buttonPing)
        val textViewResult = findViewById<TextView>(R.id.textViewResult)


        buttonPing.setOnClickListener {
            CoroutineScope(Dispatchers.IO).launch {
                try {
                    val response = RetrofitInstance.api.ping()
                    val message = if (response.isSuccessful) {
                        response.body()?.message ?: "No message"
                    } else {
                        "Error: ${response.code()}"
                    }

                    runOnUiThread {
                        textViewResult.text = message
                    }
                } catch (e: Exception) {
                    runOnUiThread {
                        textViewResult.text = "Failed: ${e.message}"
                    }
                }
            }
        }
    }
}
