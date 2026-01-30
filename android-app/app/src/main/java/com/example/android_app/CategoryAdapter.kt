package com.example.android_app

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ProgressBar
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.android_app.data.CategoryTotal
import java.util.Locale

class CategoryAdapter(private val categories: List<CategoryTotal>) :
    RecyclerView.Adapter<CategoryAdapter.CategoryViewHolder>() {

    private val maxAmount = categories.maxOfOrNull { it.total } ?: 1f

    class CategoryViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val categoryName: TextView = view.findViewById(R.id.categoryName)
        val categoryAmount: TextView = view.findViewById(R.id.categoryAmount)
        val categoryProgress: ProgressBar = view.findViewById(R.id.categoryProgress)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): CategoryViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_category, parent, false)
        return CategoryViewHolder(view)
    }

    override fun onBindViewHolder(holder: CategoryViewHolder, position: Int) {
        val category = categories[position]
        holder.categoryName.text = category.category
        holder.categoryAmount.text = String.format(Locale.US, "$%.2f", category.total)

        // Calculate progress as percentage of max
        val progress = ((category.total / maxAmount) * 100).toInt()
        holder.categoryProgress.progress = progress
    }

    override fun getItemCount() = categories.size
}
