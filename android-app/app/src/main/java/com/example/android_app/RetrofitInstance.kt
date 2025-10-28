package com.example.android_app

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object RetrofitInstance {
    val api: ApiService by lazy {
        Retrofit.Builder()
            // URL-ul serverului FastAPI
            .baseUrl("http://10.0.2.2:8000/")  // pentru emulator Android Studio
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
}
