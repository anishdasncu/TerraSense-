import { useEffect, useState } from 'react'
import { getUserId } from '../utils/user.js'

export default function Progress() {
  const [history, setHistory] = useState([])

  useEffect(() => {
    fetch(`/api/progress/${getUserId()}`)
      .then(res => res.json())
      .then(setHistory)
      .catch(err => console.error('Failed to load progress:', err))
  }, [])

  if (history.length === 0) {
    return (
      <div>
        <h1>Progress</h1>
        <p>No submissions yet — fill out the Planner questionnaire to start tracking your footprint over time.</p>
      </div>
    )
  }

  return (
    <div>
      <h1>Progress</h1>
      <ul className="progress-list">
        {history.map((entry, i) => (
          <li key={i}>
            <strong>{new Date(entry.submitted_at).toLocaleDateString()}</strong>
            {' — score '}{entry.score}
            {' — biggest factor: '}{entry.top_factor}
          </li>
        ))}
      </ul>
    </div>
  )
}
