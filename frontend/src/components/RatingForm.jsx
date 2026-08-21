import { useState } from 'react'

// This form lives inside a restaurant's map popup — restaurantId tells it
// which restaurant to submit the rating for, and onRatingSubmitted is a
// callback so the parent component can react (e.g. refetch restaurants
// to show the updated score) once a rating successfully saves.
function RatingForm({ restaurantId, onRatingSubmitted }) {
  const [nickname, setNickname] = useState('')
  const [spiceRating, setSpiceRating] = useState(3)
  const [note, setNote] = useState('')

  function handleSubmit(event) {
    event.preventDefault()

    fetch('/api/ratings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        nickname,
        spice_rating: spiceRating,
        note,
        restaurant_id: restaurantId,
      }),
    }).then(() => {
      setNickname('')
      setNote('')
      setSpiceRating(3)
      onRatingSubmitted()
    })
  }

  return (
    <form onSubmit={handleSubmit} style={{ marginTop: '8px' }}>
      <div>
        <label>
          Nickname:{' '}
          <input
            type="text"
            value={nickname}
            onChange={(event) => setNickname(event.target.value)}
            required
          />
        </label>
      </div>

      <div style={{ marginTop: '6px' }}>
        <label>
          Spice level:{' '}
          <select
            value={spiceRating}
            onChange={(event) => setSpiceRating(Number(event.target.value))}
          >
            <option value={1}>1 - barely spicy</option>
            <option value={2}>2 - mild</option>
            <option value={3}>3 - medium</option>
            <option value={4}>4 - hot</option>
            <option value={5}>5 - blazing</option>
          </select>
        </label>
      </div>

      <div style={{ marginTop: '6px' }}>
        <label>
          Note:{' '}
          <input
            type="text"
            value={note}
            onChange={(event) => setNote(event.target.value)}
            placeholder="optional"
          />
        </label>
      </div>

      <button type="submit" style={{ marginTop: '6px' }}>
        Submit rating
      </button>
    </form>
  )
}

export default RatingForm
