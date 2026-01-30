package com.example.android_app.data

import com.google.gson.annotations.SerializedName

data class UserDataSummary(
    val username: String,
    @SerializedName("total_spendings")
    val totalSpendings: Int,
    @SerializedName("total_amount")
    val totalAmount: Float,
    @SerializedName("category_breakdown")
    val categoryBreakdown: List<CategoryTotal>,
    @SerializedName("recent_spendings")
    val recentSpendings: List<SpendingResponse>,
    @SerializedName("earliest_spending")
    val earliestSpending: String?,
    @SerializedName("latest_spending")
    val latestSpending: String?
)
