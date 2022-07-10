package com.r3d1r4ph.coolalarm

import android.annotation.SuppressLint
import android.app.*
import android.content.Context
import android.content.Intent
import android.icu.util.Calendar
import android.media.AudioAttributes
import android.media.Ringtone
import android.media.RingtoneManager
import android.os.Build
import android.os.IBinder
import android.os.SystemClock
import android.util.Log
import android.widget.Toast
import androidx.core.app.NotificationCompat

const val INTENT_COMMAND = "Command"
const val INTENT_TIME = "Time"
const val INTENT_COMMAND_STOP = "Stop"

private const val NOTIFICATION_CHANNEL_GENERAL = "Checking"
private const val CODE_FOREGROUND_SERVICE = 1
private const val CODE_STOP_INTENT = 2
private const val CODE_START_INTENT = 3

fun Context.foregroundStartService(command: String, hour: Int, minute: Int, time: String, dayOfWeek: Int): PendingIntent {
    val intent = Intent(this, MyService::class.java).apply {
        putExtra(INTENT_COMMAND, command)
        putExtra(INTENT_TIME, time)
    }.let {
        PendingIntent.getForegroundService(
            this@foregroundStartService, CODE_START_INTENT, it, PendingIntent.FLAG_IMMUTABLE
        )
    }

    val alarmMgr = getSystemService(Context.ALARM_SERVICE) as AlarmManager
    alarmMgr.setRepeating(
        AlarmManager.RTC_WAKEUP,
        System.currentTimeMillis() + calculateAlarmTime(hour, minute, dayOfWeek),
        AlarmManager.INTERVAL_DAY * 7,
        intent
    )
    return intent
}

fun calculateAlarmTime(hour: Int, minute: Int, dayOfWeek: Int): Long {
    val mCalendar = Calendar.getInstance()
    val mHour = mCalendar[Calendar.HOUR_OF_DAY]
    val mMinute = mCalendar[Calendar.MINUTE]
    val mDayOfWeek = mCalendar[Calendar.DAY_OF_WEEK]

    var minuteDif = if (hour < mHour) {
        24 - (mHour - hour)
    } else {
        hour - mHour
    }
    minuteDif *= 60

    if (minute < mMinute) {
        minuteDif -= (mMinute - minute)
    } else {
        minuteDif += minute - mMinute
    }

    val dayOfWeekDiff = dayOfWeek - mDayOfWeek
    if (dayOfWeekDiff > 0) {
        minuteDif += dayOfWeekDiff * 24 * 60
    } else if (dayOfWeekDiff < 0) {
        minuteDif += dayOfWeekDiff * 24 * 60 + 7 * 24 * 60
    }

    return minuteDif.toLong() * 60000
}

class MyService : Service() {
    companion object {
        private var ringtone: Ringtone? = null
    }

    private fun getRingtone(): Ringtone? {
        if (ringtone == null) {
            ringtone = RingtoneManager.getRingtone(
                this,
                RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
            )
                .apply {
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                        isLooping = true
                    }
                }
        }

        return ringtone
    }

    override fun onBind(p0: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent, flags: Int, startId: Int): Int {
        //return super.onStartCommand(intent, flags, startId)
        val command = intent.getStringExtra(INTENT_COMMAND)
        Toast.makeText(this, "onStartCommand", Toast.LENGTH_SHORT).show()
        if (command == INTENT_COMMAND_STOP) {
            Toast.makeText(this, "Stop", Toast.LENGTH_SHORT).show()
            stopService()
            return START_NOT_STICKY
        } else {
            getRingtone()?.play()
        }
        showNotification(intent.getStringExtra(INTENT_TIME).toString())

        return START_STICKY
    }

    private fun stopService() {
        stopForeground(true)
        getRingtone()?.stop()
        stopSelf()
    }

    @SuppressLint("LaunchActivityFromNotification")
    private fun showNotification(time: String) {
        val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        val stopIntent = Intent(this, MyService::class.java).apply {
            putExtra(INTENT_COMMAND, INTENT_COMMAND_STOP)
        }

        val stopPendingIntent = PendingIntent.getService(
            this, CODE_STOP_INTENT, stopIntent, PendingIntent.FLAG_IMMUTABLE
        )

        try {
            with(
                NotificationChannel(
                    NOTIFICATION_CHANNEL_GENERAL,
                    "ALARM",
                    NotificationManager.IMPORTANCE_DEFAULT
                )
            ) {
                enableLights(false)
                setShowBadge(false)
                enableVibration(false)
                setSound(
                    RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM),
                    AudioAttributes
                        .Builder()
                        .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC)
                        .build()
                )
                lockscreenVisibility = Notification.VISIBILITY_PUBLIC
                manager.createNotificationChannel(this)
            }
        } catch (e: Exception) {
            Log.d("Error", "showNotification: ${e.localizedMessage}")
        }

        with(
            NotificationCompat.Builder(this, NOTIFICATION_CHANNEL_GENERAL)
        ) {
            setTicker(null)
            setContentTitle("Alarm")
            setContentText("Alarm Time: $time")
            setAutoCancel(false)
            setOngoing(true)
            setWhen(System.currentTimeMillis())
            setSmallIcon(R.drawable.ic_launcher_foreground)
            priority = NotificationCompat.PRIORITY_MAX
            setCategory(NotificationCompat.CATEGORY_ALARM)
            setVibrate(longArrayOf(500, 500, 500))
            addAction(
                0, "STOP", stopPendingIntent
            )
            startForeground(CODE_FOREGROUND_SERVICE, build())
        }
    }
}