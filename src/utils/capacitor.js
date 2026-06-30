// 前端调用 Capacitor 壁纸插件的辅助函数
// 只在 Capacitor 环境（手机 App）生效；浏览器环境回退到普通下载

export async function setWallpaper(imageUrl, type = 'both') {
  try {
    const cap = await import('@capacitor/core');
    if (!cap.Capacitor.isNativePlatform()) {
      throw new Error('浏览器环境');
    }
    const { Wallpaper } = await import('capacitor-wallpaper');

    // 先下载图片为 base64
    const base64 = await urlToBase64(imageUrl);

    await Wallpaper.setWallpaper({
      base64String: base64,
      // type: 'home' | 'lock' | 'both'
    });
    return { success: true };
  } catch (e) {
    console.warn('设为壁纸失败:', e);
    return { success: false, error: e.message };
  }
}

export async function saveToGallery(imageUrl, filename = 'an_wallpaper.jpg') {
  try {
    const cap = await import('@capacitor/core');
    if (!cap.Capacitor.isNativePlatform()) {
      throw new Error('浏览器环境');
    }
    // 使用 capacitor-wallpaper 或 Filesystem 都可以；这里用下载+分享简化
    const { Filesystem, Directory } = await import('@capacitor/filesystem');
    const base64 = await urlToBase64(imageUrl);
    await Filesystem.writeFile({
      path: filename,
      data: base64,
      directory: Directory.ExternalStorage,
    });
    return { success: true };
  } catch (e) {
    console.warn('保存相册失败:', e);
    return { success: false, error: e.message };
  }
}

async function urlToBase64(url) {
  const resp = await fetch(url);
  const blob = await resp.blob();
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result.split(',')[1]);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}
