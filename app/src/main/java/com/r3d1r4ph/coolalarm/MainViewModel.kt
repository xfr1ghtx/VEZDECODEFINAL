package com.r3d1r4ph.coolalarm

import androidx.compose.runtime.mutableStateListOf
import androidx.lifecycle.ViewModel

class MainViewModel : ViewModel() {

    val alarms = mutableStateListOf<AlarmItem>()
}