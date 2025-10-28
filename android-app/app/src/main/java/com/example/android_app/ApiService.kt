package com.example.android_app

import retrofit2.http.GET
import retrofit2.Response

interface ApiService {
    @GET("ping")
    suspend fun ping(): Response<PingResponse>
}
