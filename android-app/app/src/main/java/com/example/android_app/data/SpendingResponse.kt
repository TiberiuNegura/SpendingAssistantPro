package com.example.android_app.data

import com.google.gson.annotations.SerializedName

data class SpendingResponse(
    val id: Int,
    @SerializedName("user_id")
    val userId: Int,
    val category: String,
    val amount: Float,
    @SerializedName("created_at")
    val createdAt: String
)
