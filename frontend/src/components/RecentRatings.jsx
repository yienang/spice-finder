import { useEffect, useState } from 'react'

// Shows the most recent spice ratings people have submitted, across
// every restaurant — a simple activity feed, newest first.
function RecentRatings() {
  const [ratings, setRatings] = useState([])

  useEffect(() => {
    fetch('/api/ratings/recent')
      .then((response) => response.json())
      .then((data) => setRatings(data))
  }, [])

  if (ratings.length === 0) {
    return <p>No ratings yet — be the first to rate a restaurant!</p>
  }

  return (
    <ul className="recent-ratings-list">
      {ratings.map((rating) => (
        <li key={rating.id} className="recent-rating-item">
          <div className="recent-rating-top">
            <strong>{rating.restaurant_name}</strong>
            <span className="recent-rating-score">🌶️ {rating.spice_rating}/5</span>
          </div>
          <div className="recent-rating-meta">
            by {rating.nickname}
            {rating.note && <> — "{rating.note}"</>}
          </div>
        </li>
      ))}
    </ul>
  )
}

export default RecentRatings
