package com.an.wallpaper;

import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.view.WindowManager;
import android.graphics.Color;

import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.core.view.WindowInsetsControllerCompat;

import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Edge-to-edge：让内容延伸到状态栏和导航栏后面
        WindowCompat.setDecorFitsSystemWindows(getWindow(), false);

        // 状态栏透明 + 浅色图标（深色背景上用浅色图标）
        getWindow().setStatusBarColor(Color.TRANSPARENT);
        getWindow().setNavigationBarColor(Color.TRANSPARENT);

        // 导航栏：手势模式下半透明，3键模式透明
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            getWindow().setNavigationBarContrastEnforced(false);
        }

        // 状态栏图标用浅色（因为背景是深色的）
        WindowInsetsControllerCompat controller = WindowCompat.getInsetsController(getWindow(), getWindow().getDecorView());
        if (controller != null) {
            controller.setAppearanceLightStatusBars(false);  // 状态栏图标白色
            controller.setAppearanceLightNavigationBars(false); // 导航栏图标白色
        }

        // 防止内容在系统栏后面被裁切 — CSS safe-area-inset 处理
        // 在 Android 15+ 上，系统会自动报告手势导航的 inset 值

        // 亮度跟随系统
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
    }
}
