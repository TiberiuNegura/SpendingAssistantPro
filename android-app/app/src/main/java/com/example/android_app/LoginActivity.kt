package com.example.android_app

import android.content.Intent
import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import kotlinx.coroutines.*

class LoginActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Dacă e deja logat → Main
        val token = getSharedPreferences("auth", MODE_PRIVATE)
            .getString("token", null)

        if (token != null) {
            startActivity(Intent(this, MainActivity::class.java))
            finish()
            return
        }

        setContentView(R.layout.activity_login)

        findViewById<Button>(R.id.btnLogin).setOnClickListener { doLogin() }
        findViewById<TextView>(R.id.tvGoRegister).setOnClickListener {
            startActivity(Intent(this, RegisterActivity::class.java))
        }
    }

    private fun doLogin() {
        val username = findViewById<EditText>(R.id.etUsername).text.toString()
        val password = findViewById<EditText>(R.id.etPassword).text.toString()

        CoroutineScope(Dispatchers.IO).launch {
            val response = RetrofitInstance.api.login(username, password)

            withContext(Dispatchers.Main) {
                if (response.isSuccessful) {
                    val token = response.body()!!.accessToken

                    getSharedPreferences("auth", MODE_PRIVATE)
                        .edit()
                        .putString("token", token)
                        .apply()

                    Toast.makeText(this@LoginActivity, "Login success", Toast.LENGTH_SHORT).show()
                    startActivity(Intent(this@LoginActivity, MainActivity::class.java))
                    finish()
                } else {
                    Toast.makeText(this@LoginActivity, "Login failed", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
}
