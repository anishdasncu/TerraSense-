import { useState } from 'react'
import { getUserId } from '../utils/user.js'

const initialAnswers = {
  weekly_car_km: '', flights_per_year: '',
  ac_hours: '', heating: '',
  meat_meals_per_week: '', food_waste: '',
  recycling: '', plastic_use: '',
  shower_minutes: '', fixtures: '',
}

export default function Planner() {
  const [answers, setAnswers] = useState(initialAnswers)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const update = (field, value) => setAnswers({ ...answers, [field]: value })

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    const res = await fetch('/api/footprint', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: getUserId(), answers }),
    })
    setResult(await res.json())
    setLoading(false)
  }

  return (
    <div>
      <h1>Planner</h1>
      <form onSubmit={submit}>

        <fieldset>
          <legend>Transport</legend>
          <Number label="Car travel per week (km)" value={answers.weekly_car_km} onChange={v => update('weekly_car_km', v)} />
          <Number label="Flights per year" value={answers.flights_per_year} onChange={v => update('flights_per_year', v)} />
        </fieldset>

        <fieldset>
          <legend>Energy</legend>
          <Number label="AC usage per day (hours)" value={answers.ac_hours} onChange={v => update('ac_hours', v)} />
          <Select label="Heating source" value={answers.heating} onChange={v => update('heating', v)}
            options={{ gas_electric: 'Gas / electric', renewable: 'Renewable', none: 'None needed' }} />
        </fieldset>

        <fieldset>
          <legend>Diet</legend>
          <Number label="Meat meals per week" value={answers.meat_meals_per_week} onChange={v => update('meat_meals_per_week', v)} />
          <Select label="Food waste" value={answers.food_waste} onChange={v => update('food_waste', v)}
            options={{ often: 'Often throw food out', sometimes: 'Sometimes', rarely: 'Rarely' }} />
        </fieldset>

        <fieldset>
          <legend>Waste</legend>
          <Select label="Recycling habits" value={answers.recycling} onChange={v => update('recycling', v)}
            options={{ never: 'Never recycle', sometimes: 'Sometimes', always: 'Always' }} />
          <Select label="Single-use plastic" value={answers.plastic_use} onChange={v => update('plastic_use', v)}
            options={{ high: 'Use a lot', moderate: 'Some', low: 'Rarely' }} />
        </fieldset>

        <fieldset>
          <legend>Water</legend>
          <Number label="Average shower length (minutes)" value={answers.shower_minutes} onChange={v => update('shower_minutes', v)} />
          <Select label="Water-saving fixtures at home" value={answers.fixtures} onChange={v => update('fixtures', v)}
            options={{ none: 'None installed', some: 'A few', all: 'Fully fitted' }} />
        </fieldset>

        <button type="submit" disabled={loading}>{loading ? 'Calculating...' : 'Get My Footprint'}</button>
      </form>

      {result && (
        <div className="result">
          <p><strong>Overall score:</strong> {result.score} / 100</p>
          <p><strong>Biggest factor:</strong> {result.top_factor}</p>
          <p><strong>Recommendation:</strong> {result.recommendation}</p>

          <h3>Breakdown (0–100 each)</h3>
          <ul>
            {Object.entries(result.category_scores).map(([cat, val]) => (
              <li key={cat}>{cat}: {val}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

function Number({ label, value, onChange }) {
  return (
    <label>
      {label}
      <input type="number" min="0" value={value} onChange={e => onChange(e.target.value)} required />
    </label>
  )
}

function Select({ label, value, onChange, options }) {
  return (
    <label>
      {label}
      <select value={value} onChange={e => onChange(e.target.value)} required>
        <option value="">Select...</option>
        {Object.entries(options).map(([val, text]) => (
          <option key={val} value={val}>{text}</option>
        ))}
      </select>
    </label>
  )
}