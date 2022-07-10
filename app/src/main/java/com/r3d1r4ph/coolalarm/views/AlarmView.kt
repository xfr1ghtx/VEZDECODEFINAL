package com.r3d1r4ph.coolalarm.views

import android.app.TimePickerDialog
import android.icu.util.Calendar
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.RectangleShape
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.r3d1r4ph.coolalarm.AlarmItem
import com.r3d1r4ph.coolalarm.MainViewModel
import com.r3d1r4ph.coolalarm.foregroundStartService

@Composable
fun AlarmView(viewModel: MainViewModel) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(color = MaterialTheme.colors.background)
    ) {

        val mContext = LocalContext.current

        val mCalendar = Calendar.getInstance()
        val mHour = mCalendar[Calendar.HOUR_OF_DAY]
        val mMinute = mCalendar[Calendar.MINUTE]

        val mTime = remember { mutableStateOf("") }

        val mTimePickerDialog = TimePickerDialog(
            mContext,
            { _, hour: Int, minute: Int ->
                mTime.value =
                    "${if (hour / 10 == 0) "0$hour" else hour}:${if (minute / 10 == 0) "0$minute" else minute}"

                val item = AlarmItem(mTime.value, hour, minute).apply {
                    dayOfWeeks.forEachIndexed { index, dayOfWeek ->
                        dayOfWeek.intent = mContext.foregroundStartService("Start", hour, minute, mTime.value, index)
                    }
                }

                viewModel.alarms.add(item)
            },
            mHour,
            mMinute,
            true
        )

        Column(
            modifier = Modifier.fillMaxSize(),
            verticalArrangement = Arrangement.SpaceBetween,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(text = "Классный Будильник", fontSize = 30.sp)

            AlarmList(viewModel.alarms)

            Button(
                onClick = { mTimePickerDialog.show() },
                colors = ButtonDefaults.buttonColors(backgroundColor = Color(0XFF0F9D58))
            ) {
                Text(text = "Добавить будильник", color = Color.White)
            }
        }
    }
}

@Composable
fun AlarmList(list: List<AlarmItem>) {
    LazyColumn(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp)
            .height(400.dp)
    ) {
        items(list) { alarm ->
            OneAlarmView(item = alarm)
        }
    }
}