package com.example.android_app.utils

import com.example.android_app.data.ExtractionResponse
import com.example.android_app.data.ItemData
import com.google.gson.Gson
import com.google.gson.JsonObject

object DataParser {
    fun extractData(json: String): ExtractionResponse {
        val gson = Gson()
        val rootObject = gson.fromJson(json, JsonObject::class.java)

        // 1. Parse the Menu Items
        val itemList = mutableListOf<ItemData>()
        val menuArray = rootObject.getAsJsonArray("menu")

        menuArray?.forEach { element ->
            val itemObj = element.asJsonObject

            // Donut model returns lists for these fields, so we take the first item
            val name = itemObj.getAsJsonArray("nm")?.firstOrNull()?.asString?.trim() ?: "Unknown"
            val countStr = itemObj.getAsJsonArray("cnt")?.firstOrNull()?.asString?.trim() ?: "1"
            val priceStr = itemObj.getAsJsonArray("price")?.firstOrNull()?.asString?.trim() ?: "0.0"

            itemList.add(ItemData(
                name = name,
                count = countStr.toIntOrNull() ?: 1,
                price = priceStr.toDoubleOrNull() ?: 0.0
            ))
        }

        // 2. Parse the Total Price
        val totalObj = rootObject.getAsJsonObject("total")
        val totalStr = totalObj?.get("total_price")?.asString?.trim() ?: "0.0"
        val totalValue = totalStr.toDoubleOrNull() ?: 0.0

        return ExtractionResponse(items = itemList, totalPrice = totalValue)
    }
}