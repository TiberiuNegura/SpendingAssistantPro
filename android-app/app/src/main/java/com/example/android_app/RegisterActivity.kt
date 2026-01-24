package com.example.android_app

import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import kotlinx.coroutines.*

class RegisterActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_register)

        findViewById<Button>(R.id.btnRegister).setOnClickListener { doRegister() }
    }

    private fun doRegister() {
        val username = findViewById<EditText>(R.id.etUsername).text.toString()
        val password = findViewById<EditText>(R.id.etPassword).text.toString()

        CoroutineScope(Dispatchers.IO).launch {
            val response = RetrofitInstance.api.register(
                RegisterRequest(username, password)
            )

            withContext(Dispatchers.Main) {
                if (response.isSuccessful) {
                    Toast.makeText(this@RegisterActivity, "Register success", Toast.LENGTH_SHORT).show()
                    finish() // revine la Login
                } else {
                    Toast.makeText(this@RegisterActivity, "Register failed", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
}
