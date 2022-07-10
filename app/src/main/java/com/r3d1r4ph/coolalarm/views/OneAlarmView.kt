package com.r3d1r4ph.coolalarm.views

import android.app.AlarmManager
import android.content.Context
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.material.Button
import androidx.compose.material.ButtonDefaults
import androidx.compose.material.Surface
import androidx.compose.material.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.RectangleShape
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.r3d1r4ph.coolalarm.AlarmItem
import com.r3d1r4ph.coolalarm.calculateAlarmTime

@Composable
fun OneAlarmView(item: AlarmItem) {
    Surface(
        shape = RectangleShape,
        color = Color.LightGray,
        border = BorderStroke(1.dp, Color.Black),
        elevation = 2.dp,
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp)
    ) {
        val mContext = LocalContext.current
        val alarmMgr = mContext.getSystemService(Context.ALARM_SERVICE) as AlarmManager

        Column(modifier = Modifier.fillMaxSize()) {
            Text(
                text = "Будильник на: ${item.time}",
                modifier = Modifier.padding(start = 16.dp, top = 8.dp)
            )
            Spacer(modifier = Modifier.height(16.dp))
            LazyRow(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(start = 16.dp)
            ) {
                items(item.dayOfWeeks) { dayOfWeek ->
                    Button(
                        onClick = {
                            dayOfWeek.isActive.value = !dayOfWeek.isActive.value
                            if (dayOfWeek.isActive.value) {
                                alarmMgr.setRepeating(
                                    AlarmManager.RTC_WAKEUP,
                                    System.currentTimeMillis() + calculateAlarmTime(
                                        item.hour,
                                        item.minute,
                                        dayOfWeek.index
                                    ),
                                    AlarmManager.INTERVAL_DAY * 7,
                                    dayOfWeek.intent
                                )
                            } else {
                                alarmMgr.cancel(dayOfWeek.intent)
                            }
                        },
                        colors = ButtonDefaults.buttonColors(backgroundColor = if (dayOfWeek.isActive.value) Color.Green else Color.Red),
                        modifier = Modifier.padding(horizontal = 4.dp)
                    ) {
                        Text(text = dayOfWeek.dayOfWeek, color = Color.White)
                    }
                }
            }
            Spacer(modifier = Modifier.height(8.dp))
        }
    }
}

@Preview
@Composable
fun AlarmPreview() {
//    OneAlarmView(
//        AlarmItem(
//            "15:34"
//        )
//    )
}