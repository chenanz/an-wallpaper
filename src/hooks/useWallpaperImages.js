import { useEffect, useState, useRef } from 'react';
import { getFallbackImageUrl } from '../data';

const ONLINE_BASE = 'https://chenanz.github.io/an-wallpaper/';

/**
 * 轻量图片加载器：
 * - 不预加载任何图片（彻底消除启动卡顿）
 * - 直接赋 URL，让浏览器 <img loading="lazy"> + IntersectionObserver 按需加载
 * - 在线优先（CDN），离线 fallback
 * - APK 不打包图片，全部走 Pages CDN
 */
export function useWallpaperImages(data) {
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const isNative = !!(window.Capacitor && window.Capacitor.isNativePlatform && window.Capacitor.isNativePlatform());
    const localBase = import.meta.env.BASE_URL || '/';

    const result = data.map(item => {
      const filename = item.imageFile || `${item.id}.jpg`;
      // APK/原生环境：强制走 CDN（不打包图片）
      // Web/PWA：也走 CDN（GitHub Pages 托管）
      const onlineUrl = `${ONLINE_BASE}images/${filename}`;
      const localPath = isNative ? null : `${localBase}images/${filename}`;

      return {
        ...item,
        imageUrl: onlineUrl,
        thumbnailUrl: onlineUrl,
        _localPath: localPath,
      };
    });
    setImages(result);
    setLoading(false);
  }, [data]);

  // 图片加载失败时的 fallback 处理（由 <img onError> 调用）
  const handleImageError = useRef((e, item) => {
    if (!item) return;
    const target = e.target;
    // 避免无限循环：只 fallback 一次
    if (target.dataset.fallback) return;
    target.dataset.fallback = '1';

    if (item._localPath) {
      // Web 环境：尝试本地路径
      target.src = item._localPath;
    } else {
      // APK/CDN 失败：用占位图
      target.src = getFallbackImageUrl(item.id, 720, 1280);
    }
  });

  return { images, loading, handleImageError };
}
