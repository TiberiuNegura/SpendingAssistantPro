package com.example.android_app

import android.graphics.Color
import android.os.Bundle
import android.view.View
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.android_app.data.CategoryTotal
import com.github.mikephil.charting.charts.PieChart
import com.github.mikephil.charting.data.PieData
import com.github.mikephil.charting.data.PieDataSet
import com.github.mikephil.charting.data.PieEntry
import com.github.mikephil.charting.formatter.PercentFormatter
import com.github.mikephil.charting.utils.ColorTemplate
import kotlinx.coroutines.*

class StatisticsActivity : AppCompatActivity() {

    private lateinit var pieChart: PieChart
    private lateinit var balanceText: TextView
    private lateinit var categoriesRecyclerView: RecyclerView
    private lateinit var emptyState: LinearLayout

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_statistics)

        // Initialize views
        pieChart = findViewById(R.id.pieChart)
        balanceText = findViewById(R.id.balanceText)
        categoriesRecyclerView = findViewById(R.id.categoriesRecyclerView)
        emptyState = findViewById(R.id.emptyState)

        // Setup RecyclerView
        categoriesRecyclerView.layoutManager = LinearLayoutManager(this)

        // Load user statistics
        loadStatistics()
    }

    private fun loadStatistics() {
        val token = getSharedPreferences("auth", MODE_PRIVATE).getString("token", null)

        if (token == null) {
            Toast.makeText(this, "Please login first", Toast.LENGTH_SHORT).show()
            finish()
            return
        }

        CoroutineScope(Dispatchers.IO).launch {
            try {
                val response = RetrofitInstance.api.getUserData("Bearer $token")

                withContext(Dispatchers.Main) {
                    if (response.isSuccessful && response.body() != null) {
                        val userData = response.body()!!

                        if (userData.totalSpendings > 0) {
                            // Show data
                            emptyState.visibility = View.GONE
                            pieChart.visibility = View.VISIBLE
                            categoriesRecyclerView.visibility = View.VISIBLE

                            // Update total balance
                            balanceText.text = String.format("$%.2f", userData.totalAmount)

                            // Setup pie chart
                            setupPieChart(userData.categoryBreakdown)

                            // Setup categories list
                            categoriesRecyclerView.adapter = CategoryAdapter(userData.categoryBreakdown)
                        } else {
                            // Show empty state
                            emptyState.visibility = View.VISIBLE
                            pieChart.visibility = View.GONE
                            categoriesRecyclerView.visibility = View.GONE
                            balanceText.text = "$0.00"
                        }
                    } else {
                        Toast.makeText(
                            this@StatisticsActivity,
                            "Failed to load statistics",
                            Toast.LENGTH_SHORT
                        ).show()
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(
                        this@StatisticsActivity,
                        "Error: ${e.message}",
                        Toast.LENGTH_SHORT
                    ).show()
                }
            }
        }
    }

    private fun setupPieChart(categories: List<CategoryTotal>) {
        // Create entries for pie chart
        val entries = categories.map { PieEntry(it.total, it.category) }

        // Create dataset
        val dataSet = PieDataSet(entries, "Spending by Category")

        // Define beautiful colors
        val colors = listOf(
            Color.parseColor("#FF6B9D"),  // Pink
            Color.parseColor("#4ECDC4"),  // Turquoise
            Color.parseColor("#FFD93D"),  // Yellow
            Color.parseColor("#6BCF7F"),  // Green
            Color.parseColor("#95E1D3"),  // Mint
            Color.parseColor("#F38181"),  // Coral
            Color.parseColor("#AA96DA"),  // Purple
            Color.parseColor("#FCBAD3"),  // Light Pink
            Color.parseColor("#A8D8EA"),  // Sky Blue
            Color.parseColor("#FFB6B9")   // Peach
        )
        dataSet.colors = colors

        // Customize dataset
        dataSet.valueTextSize = 12f
        dataSet.valueTextColor = Color.WHITE
        dataSet.sliceSpace = 3f
        dataSet.selectionShift = 5f

        // Create pie data
        val pieData = PieData(dataSet)
        pieData.setValueFormatter(PercentFormatter(pieChart))

        // Configure chart
        pieChart.data = pieData
        pieChart.description.isEnabled = false
        pieChart.setUsePercentValues(true)
        pieChart.isDrawHoleEnabled = true
        pieChart.setHoleColor(Color.TRANSPARENT)
        pieChart.holeRadius = 40f
        pieChart.transparentCircleRadius = 45f
        pieChart.setDrawEntryLabels(true)
        pieChart.setEntryLabelColor(Color.BLACK)
        pieChart.setEntryLabelTextSize(11f)
        pieChart.legend.isEnabled = true
        pieChart.legend.textSize = 12f

        // Animate chart
        pieChart.animateY(1000)

        // Refresh
        pieChart.invalidate()
    }
}
