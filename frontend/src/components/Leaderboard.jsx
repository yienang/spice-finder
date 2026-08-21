import { useEffect, useState } from 'react'

// The "brag wall" — shows who's rated the most restaurants, ranked by
// rating_count (the backend already sorts it that way), with each
// person's average spice rating alongside.
function Leaderboard() {
  const [entries, setEntries] = useState([])

  useEffect(() => {
    fetch('/api/leaderboard')
      .then((response) => response.json())
      .then((data) => setEntries(data))
  }, [])

  if (entries.length === 0) {
    return <p>No ratings yet — be the first to rate a restaurant!</p>
  }

  return (
    <table className="leaderboard-table">
      <thead>
        <tr>
          <th>Rank</th>
          <th>Nickname</th>
          <th>Ratings submitted</th>
          <th>Average spice given</th>
        </tr>
      </thead>
      <tbody>
        {entries.map((entry, index) => (
          <tr key={entry.nickname}>
            <td>#{index + 1}</td>
            <td>{entry.nickname}</td>
            <td>{entry.rating_count}</td>
            <td>{entry.average_spice.toFixed(1)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default Leaderboard
