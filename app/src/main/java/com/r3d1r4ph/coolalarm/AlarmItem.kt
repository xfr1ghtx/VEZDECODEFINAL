package com.r3d1r4ph.coolalarm

import android.app.PendingIntent
import androidx.compose.runtime.MutableState
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.snapshots.SnapshotStateList

data class AlarmItem(
    val time: String,
    val hour: Int,
    val minute: Int,
    val dayOfWeeks: SnapshotStateList<DayOfWeek> = mutableStateListOf(
        DayOfWeek(0, "ПН"),
        DayOfWeek(1, "ВТ"),
        DayOfWeek(2, "СР"),
        DayOfWeek(3, "ЧТ"),
        DayOfWeek(4, "ПТ"),
        DayOfWeek(5, "СБ"),
        DayOfWeek(6, "ВС")
    )
)

data class DayOfWeek(
    val index: Int,
    val dayOfWeek: String,
    val isActive: MutableState<Boolean> = mutableStateOf(true),
    var intent: PendingIntent? = null
)
