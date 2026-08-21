import { useEffect } from 'react'
import { useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet.heat'

// This component draws no visible JSX of its own (see `return null`
// below) — its only job is reaching into the raw Leaflet map object
// and adding a heat-glow layer to it directly. The heatmap plugin
// isn't a React thing, it's a plain Leaflet plugin, so this is a
// "bridge" between React and that older-style library, similar to the
// marker-icon fix in RestaurantMap.jsx.
function HeatmapLayer({ restaurants }) {
  // useMap() is a react-leaflet hook that only works on a component
  // rendered INSIDE a <MapContainer> — it hands you the actual
  // underlying Leaflet map object, the same kind of object all of
  // Leaflet's plain (non-React) plugins expect to work with.
  const map = useMap()

  useEffect(() => {
    // leaflet.heat wants a plain array of [latitude, longitude, intensity]
    // triples. We skip any restaurant with no spice_score (null) since
    // there's nothing meaningful to plot for it.
    const points = restaurants
      .filter((r) => r.spice_score !== null && r.spice_score !== undefined)
      .map((r) => [r.latitude, r.longitude, r.spice_score])

    const heatLayer = L.heatLayer(points, { radius: 35, blur: 25, maxZoom: 17 })
    heatLayer.addTo(map)

    // This function runs before the effect re-runs (e.g. if restaurants
    // updates) or when the component unmounts. Without it, every re-run
    // would stack a brand new heat layer on top of the old one instead
    // of replacing it.
    return () => {
      map.removeLayer(heatLayer)
    }
  }, [restaurants, map])

  return null
}

export default HeatmapLayer
