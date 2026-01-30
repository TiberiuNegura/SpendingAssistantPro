package com.example.android_app

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object RetrofitInstance {
    // Configuration for different environments
    // For Android Emulator: use "http://10.0.2.2:8000/"
    // For Physical Device: use your computer's IP address, e.g., "http://192.168.1.9:8000/"
    private const val BASE_URL = "http://192.168.5.34:8000/"  // Change this to match your setup

    // Public accessor for the base URL
    const val baseUrl = BASE_URL

    val api: ApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
}
