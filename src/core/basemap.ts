import type { StyleSpecification } from 'mapbox-gl';

const AMAP_HOSTS = ['01', '02', '03', '04'] as const;

/**
 * Gaode raster tiles. Carto's free tiles now return an "API key required"
 * watermark, and OpenFreeMap is often unreachable.
 */
export function amapRasterStyle(): StyleSpecification {
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
    layers: [{ id: 'amap', type: 'raster', source: 'amap' }],
  };
}
