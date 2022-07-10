package com.r3d1r4ph.coolalarm.screens

import androidx.compose.runtime.Composable
import androidx.compose.ui.tooling.preview.Preview
import com.r3d1r4ph.coolalarm.MainViewModel
import com.r3d1r4ph.coolalarm.views.AlarmView

@Composable
fun AlarmScreen(viewModel: MainViewModel = MainViewModel()) {
    AlarmView(viewModel)
}

@Preview
@Composable
fun AlarmPreview() {
    AlarmScreen()
}