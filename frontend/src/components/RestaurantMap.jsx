import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import HeatmapLayer from './HeatmapLayer'

// Leaflet's default marker icon references image files in a way that
// breaks when bundled by Vite (a known, slightly obscure compatibility
// quirk — not something you did wrong). This block works around it by
// pointing the default icon at hosted copies of the same images instead.
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const BRISBANE_CENTER = [-27.4705, 153.0260]

function RestaurantMap() {
  // Same useState + useEffect + fetch pattern from App.jsx's backend
  // health check — except this time we're storing a whole array of
  // restaurants instead of one status string.
  const [restaurants, setRestaurants] = useState([])

  useEffect(() => {
    fetch('/api/restaurants')
      .then((response) => response.json())
      .then((data) => setRestaurants(data))
  }, [])

  return (
    <MapContainer center={BRISBANE_CENTER} zoom={13} style={{ height: '600px', width: '100%' }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />

      {restaurants.map((restaurant) => (
        <Marker key={restaurant.id} position={[restaurant.latitude, restaurant.longitude]}>
          <Popup>
            {restaurant.name} — spice: {restaurant.spice_score}
          </Popup>
        </Marker>
      ))}

      <HeatmapLayer restaurants={restaurants} />
    </MapContainer>
  )
}

export default RestaurantMap
