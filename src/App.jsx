import React, { useState, useCallback, useEffect, memo, useRef } from 'react';
import { useLocalStorage } from './hooks/useLocalStorage';
import { useWallpaperImages } from './hooks/useWallpaperImages';
import { setWallpaper, saveToGallery } from './utils/capacitor';
import {
  wallpaperData,
  GAMES,
  STYLES,
} from './data';

const isNative = !!(window.Capacitor && window.Capacitor.isNativePlatform && window.Capacitor.isNativePlatform());

export default function App() {
  const { images, loading } = useWallpaperImages(wallpaperData);
  const [tab, setTab] = useState('home');
  const [viewer, setViewer] = useState(null);
  const [subPage, setSubPage] = useState(null);
  const [favorites, setFavorites] = useLocalStorage('an_favorites', []);
  const [lastBack, setLastBack] = useState(0);

  const toggleFavorite = useCallback((id) => {
    setFavorites(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
  }, [setFavorites]);

  const isFav = useCallback((id) => favorites.includes(id), [favorites]);

  useEffect(() => {
    if (!isNative) return;
    let AppPlugin;
    try { AppPlugin = window.Capacitor.Plugins.App; } catch { return; }
    if (!AppPlugin) return;
    const handler = AppPlugin.addListener('backButton', () => {
      if (viewer) { setViewer(null); return; }
      if (subPage) { setSubPage(false); return; }
      if (tab !== 'home') { setTab('home'); return; }
      const now = Date.now();
      if (now - lastBack < 2000) { AppPlugin.exitApp?.(); }
      else { setLastBack(now); showToast('再按一次退出'); }
    });
    return () => handler?.then?.(h => h?.remove?.()) || handler?.remove?.();
  }, [viewer, subPage, tab, lastBack]);

  if (loading) {
    return (
      <div className="app-root bg-app-bg flex items-center justify-center text-app-muted">
        <div className="w-10 h-10 border-2 border-app-accent border-t-transparent rounded-full animate-spin mb-3" />
        <span className="text-sm">正在加载壁纸…</span>
      </div>
    );
  }

  return (
    <div className="app-root bg-app-bg">
      {/* 主内容区：唯一滚动容器 */}
      <div className="app-content">
        {tab === 'home' && <HomePage images={images} openViewer={setViewer} isFav={isFav} toggleFavorite={toggleFavorite} />}
        {tab === 'style' && <StylePage images={images} openViewer={setViewer} isFav={isFav} toggleFavorite={toggleFavorite} />}
        {tab === 'char' && <CharacterPage images={images} openViewer={setViewer} isFav={isFav} toggleFavorite={toggleFavorite} onSubPage={setSubPage} />}
        {tab === 'me' && <MePage images={images} favorites={favorites} toggleFavorite={toggleFavorite} setViewer={setViewer} />}
      </div>

      {/* 底部导航：fixed 在底部 */}
      <nav className="app-nav glass border-t border-app-border flex items-center justify-around z-40">
        <TabBtn label="首页" icon="🏠" active={tab==='home'} onClick={()=>setTab('home')} />
        <TabBtn label="风格" icon="🎨" active={tab==='style'} onClick={()=>setTab('style')} />
        <TabBtn label="角色" icon="👤" active={tab==='char'} onClick={()=>setTab('char')} />
        <TabBtn label="我的" icon="💜" active={tab==='me'} onClick={()=>setTab('me')} />
      </nav>

      {viewer && <ImageViewer wp={viewer} onClose={()=>setViewer(null)} isFav={isFav(viewer.id)} toggleFavorite={()=>toggleFavorite(viewer.id)} />}
    </div>
  );
}

function TabBtn({ label, icon, active, onClick }) {
  return (
    <button onClick={onClick} className={`flex flex-col items-center justify-center w-16 h-full transition-colors ${active ? 'text-app-accent' : 'text-app-muted'}`}>
      <span className="text-lg leading-none">{icon}</span>
      <span className="text-[10px] mt-0.5 font-medium">{label}</span>
      {active && <div className="w-1 h-1 rounded-full bg-app-neon mt-0.5 shadow-[0_0_6px_#ff4ecd]" />}
    </button>
  );
}

function searchWallpapers(data, query) {
  let base = data.filter(i => i.gender === '女' && i.game !== '足社');
  if (!query || query.trim() === '') return base;
  const q = query.toLowerCase().trim();
  if (['男','male','boy','man','guy'].includes(q)) return [];
  // 搜索时才允许搜到足社内容（用户主动搜时才显示）
  if (q.includes('足社') || q.includes('足') || q.includes('裸足') || q.includes('黑丝') || q.includes('白丝') || q.includes('连裤袜') || q.includes('过膝袜')) {
    base = data.filter(i => i.gender === '女');
  }
  return base.filter(item =>
    item.title.toLowerCase().includes(q) ||
    item.characterName.toLowerCase().includes(q) ||
    item.game.toLowerCase().includes(q) ||
    item.style.toLowerCase().includes(q) ||
    item.tags.some(t => t.toLowerCase().includes(q))
  );
}

// ========== 首页 ==========
function HomePage({ images, openViewer, isFav, toggleFavorite }) {
  const [query, setQuery] = useState('');
  const [activeGame, setActiveGame] = useState(null);

  let filtered = searchWallpapers(images, query);
  if (activeGame) filtered = filtered.filter(i => i.game === activeGame);
  filtered.sort((a, b) => (b.likes || 0) - (a.likes || 0));

  return (
    <>
      {/* sticky 头部：不会随内容滚走 */}
      <div className="sticky top-0 z-10 bg-app-bg/95 backdrop-blur-sm status-bar-safe">
        <div className="px-3 pt-3 pb-2">
          <div className="flex items-center bg-app-card rounded-xl px-3 py-2.5 border border-app-border focus-within:border-app-accent transition-colors">
            <span className="text-app-muted mr-2 text-base">🔍</span>
            <input value={query} onChange={e => setQuery(e.target.value)} placeholder="搜角色名/游戏名，如 雷电将军 原神" className="flex-1 bg-transparent text-sm text-app-text placeholder:text-app-muted outline-none" />
            {query && <button onClick={() => setQuery('')} className="text-app-muted text-xs ml-2">✕</button>}
          </div>
        </div>
        <div className="px-3 pb-2">
          <div className="flex gap-2 overflow-x-auto hide-scrollbar">
            {GAMES.map(g => (
              <button key={g.id} onClick={() => setActiveGame(prev => prev === g.name ? null : g.name)} className={`shrink-0 px-3 py-1.5 rounded-full text-xs font-semibold border transition-all ${activeGame === g.name ? 'bg-app-accent/20 border-app-accent text-app-accent shadow-[0_0_8px_rgba(192,132,252,0.25)]' : 'bg-app-surface border-app-border text-app-muted hover:border-app-accent/50'}`}>
                {g.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 瀑布流内容 — 在同一个滚动容器里 */}
      <div className="px-3">
        <div className="text-xs text-app-muted mb-2">按热度排序 · {filtered.length} 张 {activeGame && `· 「${activeGame}」`}</div>
        {filtered.length === 0 ? (
          <EmptyState text={query ? `未找到「${query}」相关结果` : '暂无壁纸'} />
        ) : (
          <MasonryGrid items={filtered} openViewer={openViewer} isFav={isFav} toggleFavorite={toggleFavorite} />
        )}
      </div>
      <div className="h-20" /> {/* 底部留白给导航栏 */}
    </>
  );
}

// ========== 风格 ==========
function StylePage({ images, openViewer, isFav, toggleFavorite }) {
  const [activeStyle, setActiveStyle] = useState('3D渲染');
  const filtered = images.filter(wp => wp.style === activeStyle && wp.gender === '女');

  return (
    <>
      <div className="sticky top-0 z-10 bg-app-bg/95 backdrop-blur-sm status-bar-safe">
        <div className="px-3 pt-3 pb-2">
          <div className="flex bg-app-card rounded-xl p-1 border border-app-border">
            {STYLES.map(s => (
              <button key={s} onClick={() => setActiveStyle(s)} className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all ${activeStyle === s ? 'bg-app-accent/20 text-app-accent shadow-[0_0_6px_rgba(192,132,252,0.2)]' : 'text-app-muted hover:text-app-text'}`}>
                {s}
              </button>
            ))}
          </div>
        </div>
      </div>
      <div className="px-3">
        <div className="text-xs text-app-muted mb-2">{activeStyle} · {filtered.length} 张</div>
        {filtered.length === 0 ? <EmptyState text={`暂无 ${activeStyle} 风格壁纸`} /> : (
          <div className="grid grid-cols-2 gap-2.5">
            {filtered.map(wp => <WallpaperCard key={wp.id} wp={wp} onClick={() => openViewer(wp)} isFav={isFav(wp.id)} toggleFavorite={() => toggleFavorite(wp.id)} />)}
          </div>
        )}
      </div>
      <div className="h-20" />
    </>
  );
}

// ========== 角色 ==========
function CharacterPage({ images, openViewer, isFav, toggleFavorite, onSubPage }) {
  const [selectedGame, setSelectedGame] = useState(GAMES[0]?.name);
  const [selectedChar, setSelectedChar] = useState(null);
  const gameChars = Array.from(new Set(images.filter(i => i.game === selectedGame && i.gender === '女').map(i => i.characterName)));

  useEffect(() => { onSubPage?.(selectedChar ? 'char-detail' : null); }, [selectedChar, onSubPage]);

  if (selectedChar) {
    const charWalls = images.filter(i => i.characterName === selectedChar && i.gender === '女');
    return (
      <>
        <div className="sticky top-0 z-10 bg-app-bg/95 backdrop-blur-sm status-bar-safe">
          <div className="px-3 pt-3 pb-2 flex items-center gap-2">
            <button onClick={() => setSelectedChar(null)} className="text-app-text text-lg w-8 h-8 flex items-center justify-center rounded-full bg-app-card border border-app-border">←</button>
            <span className="text-sm font-bold text-app-text">{selectedChar}</span>
          </div>
        </div>
        <div className="px-3">
          <MasonryGrid items={charWalls} openViewer={openViewer} isFav={isFav} toggleFavorite={toggleFavorite} />
        </div>
        <div className="h-20" />
      </>
    );
  }

  return (
    <div className="flex h-full">
      <div className="char-sidebar">
        <div className="status-bar-safe" />
        {GAMES.map(g => (
          <button key={g.id} onClick={() => setSelectedGame(g.name)} className={`w-full px-2 py-3 text-[11px] leading-tight text-center transition-colors ${selectedGame === g.name ? 'text-app-accent bg-app-accent/10 border-l-2 border-app-accent' : 'text-app-muted'}`}>
            {g.name}
          </button>
        ))}
      </div>
      <div className="flex-1 overflow-y-auto overscroll-contain hide-scrollbar p-3" style={{ WebkitOverflowScrolling: 'touch', touchAction: 'pan-y' }}>
        <div className="text-xs text-app-muted mb-2">{selectedGame} · {gameChars.length} 位</div>
        {gameChars.length === 0 ? <EmptyState text="该游戏暂无收录角色" /> : (
          <div className="grid grid-cols-3 gap-3">
            {gameChars.map(char => {
              const first = images.find(i => i.characterName === char);
              return (
                <button key={char} onClick={() => setSelectedChar(char)} className="flex flex-col items-center gap-1.5 p-2 rounded-xl bg-app-surface border border-app-border hover:border-app-accent/50 transition-colors card-hover">
                  <div className="w-14 h-14 rounded-full overflow-hidden border-2 border-app-border bg-app-card">
                    <img src={first?.thumbnailUrl || first?.imageUrl} alt={char} className="w-full h-full object-cover" loading="lazy" decoding="async" />
                  </div>
                  <div className="text-[11px] text-app-text font-medium truncate w-full text-center">{char}</div>
                </button>
              );
            })}
          </div>
        )}
        <div className="h-20" />
      </div>
    </div>
  );
}

// ========== 我的（含隐藏玉足社） ==========
function MePage({ images, favorites, toggleFavorite, setViewer }) {
  const [showYuzu, setShowYuzu] = useState(false);
  const tapRef = useRef(0);

  const favWalls = images.filter(wp => favorites.includes(wp.id));
  const favByChar = {};
  favWalls.forEach(wp => {
    if (!favByChar[wp.characterName]) favByChar[wp.characterName] = [];
    favByChar[wp.characterName].push(wp);
  });

  // 玉足社壁纸筛选
  const yuzuWalls = images.filter(wp => {
    if (wp.gender !== '女') return false;
    const txt = ((wp.tags || []).join(' ') + ' ' + (wp.title || '') + ' ' + (wp.characterName || '')).toLowerCase();
    return ['足', '脚', '腿', 'foot', 'leg', 'feet', 'stocking', 'pantyhose', '裸足', '丝袜', '玉足', '脚趾', '美腿', '长腿', '黑丝', '白丝', '过膝袜', 'thigh', 'soles', '踝'].some(k => txt.includes(k));
  });

  return (
    <>
      <div className="sticky top-0 z-10 bg-app-bg/95 backdrop-blur-sm status-bar-safe">
        <div className="px-4 pt-4 pb-2">
          <h1 className="text-lg font-bold text-app-text">我的</h1>
          <p className="text-xs text-app-muted mt-0.5">收藏 · 设置</p>
        </div>
        <div className="px-3 pb-2 border-b border-app-border flex gap-4 items-center">
          <span className="text-sm font-semibold text-app-accent">收藏</span>
          <span className="text-sm font-semibold text-app-muted">设置</span>
        </div>
      </div>

      <div className="px-3 py-3">
        {/* 玉足社隐藏入口：标题「我的」连续点击5次 */}
        {/* 入口方式：在任何空白处快速连续点击5次 */}
        <div
          className="fixed top-0 left-0 w-16 h-16 z-30 opacity-0"
          onClick={() => {
            tapRef.current++;
            if (tapRef.current >= 5) {
              setShowYuzu(v => !v);
              tapRef.current = 0;
              showToast(showYuzu ? '玉足社已隐藏' : '🌿 玉足社已解锁');
            }
            setTimeout(() => { tapRef.current = 0; }, 2000);
          }}
        />

        {showYuzu && (
          <div className="mb-5">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-1.5">
                <span className="text-sm font-bold bg-gradient-to-r from-pink-400 to-purple-400 bg-clip-text text-transparent">🌿 玉足社</span>
                <span className="text-[9px] text-app-muted px-1.5 py-0.5 rounded bg-app-surface border border-app-border">{yuzuWalls.length} 张</span>
              </div>
              <button onClick={() => setShowYuzu(false)} className="text-[10px] text-app-muted border border-app-border px-2 py-0.5 rounded-full">隐藏</button>
            </div>
            {yuzuWalls.length > 0 ? (
              <MasonryGrid items={yuzuWalls} openViewer={setViewer} isFav={() => false} toggleFavorite={() => {}} />
            ) : (
              <div className="px-3 py-4 rounded-xl bg-app-card border border-app-border text-center">
                <div className="text-sm text-app-muted">🌿 暂未收录足部壁纸</div>
                <div className="text-[10px] text-app-muted/60 mt-1">爬虫持续收集中，稍后再来</div>
              </div>
            )}
          </div>
        )}

        {Object.keys(favByChar).length === 0 && !showYuzu ? (
          <EmptyState text="还没有收藏任何壁纸" />
        ) : (
          Object.entries(favByChar).map(([charName, list]) => (
            <div key={charName} className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-bold text-app-text">{charName}</span>
                <button onClick={() => list.forEach(wp => toggleFavorite(wp.id))} className="text-[10px] text-app-neon border border-app-neon/30 px-2 py-0.5 rounded-full">全部取消</button>
              </div>
              <div className="grid grid-cols-2 gap-2">
                {list.map(wp => <WallpaperCard key={wp.id} wp={wp} onClick={() => {}} isFav={true} toggleFavorite={() => toggleFavorite(wp.id)} />)}
              </div>
            </div>
          ))
        )}
      </div>
      <div className="h-20" />
    </>
  );
}

// ========== 双列瀑布流 ==========
function MasonryGrid({ items, openViewer, isFav, toggleFavorite }) {
  const left = [], right = [];
  items.forEach((item, i) => {
    if (i % 2 === 0) left.push(item);
    else right.push(item);
  });

  return (
    <div className="flex gap-2.5">
      <div className="flex-1 flex flex-col gap-2.5">
        {left.map(wp => <WallpaperCard key={wp.id} wp={wp} onClick={() => openViewer(wp)} isFav={isFav(wp.id)} toggleFavorite={() => toggleFavorite(wp.id)} />)}
      </div>
      <div className="flex-1 flex flex-col gap-2.5">
        {right.map(wp => <WallpaperCard key={wp.id} wp={wp} onClick={() => openViewer(wp)} isFav={isFav(wp.id)} toggleFavorite={() => toggleFavorite(wp.id)} />)}
      </div>
    </div>
  );
}

// ========== 壁纸卡片 ==========
const WallpaperCard = memo(function WallpaperCard({ wp, onClick, isFav, toggleFavorite }) {
  const handleImgError = useCallback((e) => {
    const target = e.target;
    if (target.dataset.fallback) return;
    target.dataset.fallback = '1';
    if (wp._localPath && target.src !== wp._localPath) target.src = wp._localPath;
  }, [wp._localPath]);

  return (
    <div className="rounded-xl overflow-hidden bg-app-card border border-app-border card-hover">
      <div className="relative cursor-pointer" onClick={onClick}>
        <div className="bg-app-surface min-h-[100px]">
          <img src={wp.thumbnailUrl || wp.imageUrl} alt={wp.title} className="w-full block" loading="lazy" decoding="async" onError={handleImgError} />
        </div>
        {wp.source && wp.source !== '官方' && (
          <div className="absolute top-1.5 left-1.5 bg-black/60 backdrop-blur rounded px-1.5 py-0.5 text-[9px] text-app-cyan border border-app-cyan/30">{wp.source}</div>
        )}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent px-2 pb-1.5 pt-6">
          <div className="text-[11px] text-white font-semibold truncate">{wp.title}</div>
          <div className="flex items-center justify-between mt-0.5">
            <span className="text-[9px] text-white/70">{wp.characterName}</span>
            <span className="text-[9px] text-white/50">❤️ {wp.likes || 0}</span>
          </div>
        </div>
      </div>
      <div className="flex items-center justify-between px-2 py-1.5">
        <div className="flex items-center gap-1">
          <span className="text-[9px] px-1 py-0.5 rounded bg-app-surface text-app-muted border border-app-border">{wp.game.slice(0, 4)}</span>
          <span className="text-[9px] px-1 py-0.5 rounded bg-app-surface text-app-accent border border-app-accent/20">{wp.style}</span>
        </div>
        <button onClick={(e) => { e.stopPropagation(); toggleFavorite(); }} className={`text-lg transition-transform active:scale-90 ${isFav ? 'text-app-liked drop-shadow-[0_0_6px_#ff2d8a]' : 'text-app-muted'}`}>
          {isFav ? '❤️' : '🤍'}
        </button>
      </div>
    </div>
  );
});

function EmptyState({ text }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-app-muted">
      <div className="text-3xl mb-2 opacity-50">🍃</div>
      <div className="text-sm">{text}</div>
    </div>
  );
}

// ========== 全屏预览 ==========
function ImageViewer({ wp, onClose, isFav, toggleFavorite }) {
  const [loaded, setLoaded] = useState(false);

  return (
    <div className="fixed inset-0 z-50 bg-black flex flex-col animate-fade-in">
      <div className="absolute top-0 left-0 right-0 z-10 flex items-center px-3 status-bar-safe" style={{ paddingTop: 'max(env(safe-area-inset-top, 0px), 12px)', paddingBottom: 8, background: 'linear-gradient(to bottom, rgba(0,0,0,0.7), transparent)' }}>
        <button onClick={onClose} className="w-9 h-9 rounded-full bg-white/10 backdrop-blur flex items-center justify-center text-white text-lg">✕</button>
      </div>
      <div className="flex-1 flex items-center justify-center overflow-hidden min-h-0">
        {!loaded && (
          <div className="flex flex-col items-center gap-3">
            <div className="w-10 h-10 border-2 border-app-accent border-t-transparent rounded-full animate-spin" />
            <div className="text-xs text-white/50">加载中…</div>
          </div>
        )}
        <img src={wp.imageUrl} alt={wp.title} className={`max-w-full max-h-full object-contain ${loaded ? 'fade-in' : 'hidden'}`} onLoad={() => setLoaded(true)} />
      </div>
      <div className="shrink-0 safe-bottom" style={{ background: 'linear-gradient(to top, black, rgba(0,0,0,0.8), transparent)', paddingTop: 24, paddingBottom: 'max(env(safe-area-inset-bottom, 0px), 24px)', paddingLeft: 16, paddingRight: 16 }}>
        <div className="text-sm font-bold text-white mb-1">{wp.title}</div>
        <div className="text-xs text-white/60 mb-4">{wp.characterName} · {wp.game} · {wp.style}</div>
        <div className="flex items-center justify-around">
          <ActionBtn icon="💾" label="设为壁纸" onClick={async () => { showToast('正在设置壁纸…'); const res = await setWallpaper(wp.imageUrl); showToast(res.success ? '壁纸已设置' : `暂不支持（${res.error}）`); }} />
          <ActionBtn icon="⬇️" label="下载原图" onClick={async () => {
            const fname = `${wp.title}_${wp.id}.jpg`;
            const res = await saveToGallery(wp.imageUrl, fname);
            if (!res.success && res.error?.includes('浏览器')) { const a = document.createElement('a'); a.href = wp.imageUrl; a.download = fname; a.target = '_blank'; a.click(); showToast('已触发下载'); }
            else { showToast(res.success ? '已保存到相册' : `保存失败：${res.error}`); }
          }} />
          <ActionBtn icon={isFav ? '❤️' : '🤍'} label={isFav ? '已收藏' : '收藏'} active={isFav} onClick={toggleFavorite} />
        </div>
        {wp.pixiv_url && <div className="text-center mt-3"><a href={wp.pixiv_url} target="_blank" rel="noopener" className="text-[10px] text-app-cyan underline">Pixiv #{wp.pixiv_id}</a></div>}
        {wp.miyoushe_post_id && <div className="text-center mt-2"><a href={`https://www.miyoushe.com/ys/article/${wp.miyoushe_post_id}`} target="_blank" rel="noopener" className="text-[10px] text-app-neon underline">米游社 #{wp.miyoushe_post_id}</a></div>}
      </div>
    </div>
  );
}

function ActionBtn({ icon, label, onClick, active }) {
  return (
    <button onClick={onClick} className="flex flex-col items-center gap-1 min-w-[72px]">
      <div className={`w-12 h-12 rounded-full flex items-center justify-center text-xl border transition-all ${active ? 'bg-app-neon/20 border-app-neon text-app-neon' : 'bg-white/10 border-white/20 text-white'}`}>{icon}</div>
      <span className={`text-[10px] ${active ? 'text-app-neon' : 'text-white/70'}`}>{label}</span>
    </button>
  );
}

function showToast(msg) {
  document.querySelectorAll('.app-toast').forEach(e => e.remove());
  const el = document.createElement('div');
  el.className = 'app-toast fixed top-16 left-1/2 -translate-x-1/2 bg-app-card border border-app-border text-app-text text-xs px-4 py-2 rounded-full z-[60] animate-fade-in shadow-lg';
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 2000);
}
