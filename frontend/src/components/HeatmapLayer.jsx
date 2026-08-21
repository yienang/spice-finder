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

    const heatLayer = L.heatLayer(points, {
      // How far each individual restaurant's glow spreads out in pixels
      // before fading to nothing. Lower = each point stays smaller and
      // more contained, less likely to blend into neighboring points.
      radius: 22,
      // leaflet.heat actually does two separate things: each point gets
      // its own smooth radial gradient (bright center fading to
      // transparent edge — like a contour/elevation shading), and THEN,
      // separately, a blur filter gets passed over the whole canvas on
      // top of that. That second pass is what was making edges look
      // hazy/smudged like fog. Setting blur to 0 skips that second pass
      // entirely — you're left with just the underlying radial-gradient
      // falloff, which is smooth but not fuzzy, closer to how a
      // topographic map shades elevation by distance.
      blur: 0,
      maxZoom: 17,
      // This is going back to 5 (the real top of the spice_score scale)
      // instead of 2. Here's why: the gradient below picks colors based
      // on normalized intensity, i.e. score / max. With max at 2, a
      // score of 2 counted as 100% intensity (maroon) — but so did a
      // score of 1.5, since anything near the max gets crushed toward
      // the top of the gradient. That's why everything was reading as
      // dark red: scores that aren't even that spicy were still landing
      // near the top of a too-short scale. Using the real max of 5
      // spreads scores out properly, so a "5" restaurant looks distinctly
      // more intense than a "3" one instead of them blurring together.
      max: 5,
      // minOpacity keeps even low-intensity points from fading to
      // near-invisible — without it, faint points can disappear
      // entirely rather than showing as a pale red.
      minOpacity: 0.4,
      // Now that max is 5, each gradient stop lines up directly with an
      // actual spice_score value (score / 5 = the stop's position) —
      // so this is literally "what color is a 1, a 2, a 3...":
      //   score 1 (0.2) -> very light orange
      //   score 2 (0.4) -> light orange
      //   score 3 (0.6) -> orange
      //   score 4 (0.8) -> red
      //   score 5 (1.0) -> a maroon-purple blend
      gradient: {
        0.0: 'rgba(255, 243, 214, 0)',
        0.2: '#ffedc2',
        0.4: '#fed976',
        0.6: '#f57c00',
        0.8: '#d32f2f',
        1.0: '#6b0f3a',
      },
    })
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
