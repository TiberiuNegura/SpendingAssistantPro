package com.example.android_app

import com.example.android_app.data.PingResponse
import com.example.android_app.data.UserDataSummary
import retrofit2.http.GET
import retrofit2.Response
import retrofit2.http.*

interface ApiService {
    @GET("ping")
    suspend fun ping(): Response<PingResponse>

    // LOGIN - FORM
    @FormUrlEncoded
    @POST("auth/login")
    suspend fun login(
        @Field("username") username: String,
        @Field("password") password: String
    ): Response<LoginResponse>

    // REGISTER - JSON
    @POST("auth/register")
    suspend fun register(
        @Body request: RegisterRequest
    ): Response<GenericResponse>

    // STATISTICS - Get user data summary
    @GET("user/data")
    suspend fun getUserData(
        @Header("Authorization") token: String
    ): Response<UserDataSummary>
}
