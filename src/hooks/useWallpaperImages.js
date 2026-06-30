import { useEffect, useState, useRef } from 'react';
import { getFallbackImageUrl } from '../data';

const ONLINE_BASE = 'https://chenanz.github.io/an-wallpaper/';

/**
 * 轻量图片加载器：
 * - 不预加载任何图片（彻底消除启动卡顿）
 * - 直接赋 URL，让浏览器 <img loading="lazy"> + IntersectionObserver 按需加载
 * - 在线优先，离线 fallback
 */
export function useWallpaperImages(data) {
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 直接构造 URL 列表，不做任何预加载
    const localBase = import.meta.env.BASE_URL || '/';
    const result = data.map(item => {
      const filename = item.imageFile || `${item.id}.jpg`;
      const onlineUrl = `${ONLINE_BASE}images/${filename}`;
      const localPath = `${localBase}images/${filename}`;
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
      target.src = item._localPath;
    } else {
      target.src = getFallbackImageUrl(item.id, 720, 1280);
    }
  });

  return { images, loading, handleImageError };
}
