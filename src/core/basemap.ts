import type { StyleSpecification } from 'mapbox-gl';

const AMAP_HOSTS = ['01', '02', '03', '04'] as const;

/**
 * Gaode road tiles, flattened to a CARTO-like gray.
 * The source image is colorful; raster paint drops rivers and province
 * borders down to a faint gray so the route stays visible.
 */
export function amapRasterStyle(dark: boolean): StyleSpecification {
  const paint = dark
    ? {
        'raster-saturation': -1,
        'raster-contrast': -0.62,
        'raster-brightness-min': 0.26,
        'raster-brightness-max': 0.055,
      }
    : {
        'raster-saturation': -1,
        'raster-contrast': -0.72,
        'raster-brightness-min': 0.9,
        'raster-brightness-max': 1,
      };
  return {
    version: 8,
    sources: {
      amap: {
        type: 'raster',
        tiles: AMAP_HOSTS.map(
          (host) =>
            `https://webrd${host}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}`
        ),
        tileSize: 256,
        maxzoom: 18,
        attribution: '© 高德地图',
      },
    },
    layers: [
      {
        id: 'background',
        type: 'background',
        paint: { 'background-color': dark ? '#1e1e1e' : '#f5f5f5' },
      },
      { id: 'amap', type: 'raster', source: 'amap', paint },
    ],
  };
}
