/**
 * extract-assets.js — asset discovery (from ai-website-cloner-template, MIT).
 * Run via browser console / Playwright evaluate on a loaded page.
 * Returns: images (with layered-composition context), videos, background
 * images, SVG count, fonts, favicons.
 */
(() => {
  return {
    images: [...document.querySelectorAll('img')].map(img => ({
      src: img.src || img.currentSrc,
      alt: img.alt,
      width: img.naturalWidth,
      height: img.naturalHeight,
      // Include parent info to detect layered compositions
      parentClasses: img.parentElement?.className,
      siblings: img.parentElement ? [...img.parentElement.querySelectorAll('img')].length : 0,
      position: getComputedStyle(img).position,
      zIndex: getComputedStyle(img).zIndex
    })),
    videos: [...document.querySelectorAll('video')].map(v => ({
      src: v.src || v.querySelector('source')?.src,
      poster: v.poster,
      autoplay: v.autoplay,
      loop: v.loop,
      muted: v.muted
    })),
    backgroundImages: [...document.querySelectorAll('*')].filter(el => {
      const bg = getComputedStyle(el).backgroundImage;
      return bg && bg !== 'none';
    }).map(el => ({
      url: getComputedStyle(el).backgroundImage,
      element: el.tagName + '.' + el.className?.split(' ')[0]
    })),
    svgCount: document.querySelectorAll('svg').length,
    fonts: [...new Set([...document.querySelectorAll('*')].slice(0, 200).map(el => getComputedStyle(el).fontFamily))],
    favicons: [...document.querySelectorAll('link[rel*="icon"]')].map(l => ({ href: l.href, sizes: l.sizes?.toString() }))
  };
})()
