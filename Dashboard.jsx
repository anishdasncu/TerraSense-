import { useEffect, useState } from 'react'

export default function Dashboard() {
  const [data, setData] = useState(null)

  useEffect(() => {
    fetch('/api/dashboard')
      .then(res => res.json())
      .then(setData)
      .catch(err => console.error('Failed to load dashboard:', err))
  }, [])

  if (!data) return <p>Loading...</p>

  return (
    <div>
      <h1>Dashboard</h1>

      <h2>Weather</h2>
      <div className="grid">
        <Card title="Temperature" value={`${data.weather.temperature.value}${data.weather.temperature.unit}`} />
        <Card title="Humidity" value={`${data.weather.humidity.value}${data.weather.humidity.unit}`} />
        <Card title="Pressure" value={`${data.weather.pressure.value} ${data.weather.pressure.unit}`} />
        <Card title="Wind Speed" value={`${data.weather.wind_speed.value} ${data.weather.wind_speed.unit}`} />
        <Card title="Wind Direction" value={data.weather.wind_direction.value} />
        <Card title="Rainfall" value={`${data.weather.rainfall.value}`} />
        <Card title="Cloud Cover" value={`${data.weather.cloud_cover.value}${data.weather.cloud_cover.unit}`} />
        <Card title="Heatwave Risk" value={data.heatwave_risk.level} sub={data.heatwave_risk.reason} />
      </div>

      <h2>Air Quality</h2>
      <div className="grid">
        <Card title="PM2.5" value={`${data.air_quality.pm2_5.value} ${data.air_quality.pm2_5.unit}`} />
        <Card title="PM10" value={`${data.air_quality.pm10.value} ${data.air_quality.pm10.unit}`} />
        <Card title="CO" value={`${data.air_quality.co.value} ${data.air_quality.co.unit}`} />
        <Card title="NO₂" value={`${data.air_quality.no2.value} ${data.air_quality.no2.unit}`} />
        <Card title="SO₂" value={`${data.air_quality.so2.value} ${data.air_quality.so2.unit}`} />
        <Card title="AQI Category" value={data.air_quality.aqi_category} />
        <Card title="Environmental Risk" value={`${data.environmental_risk_category} (${data.environmental_risk_score})`} />
      </div>
    </div>
  )
}

function Card({ title, value, sub }) {
  return (
    <div className="card">
      <h3>{title}</h3>
      <p>{value}</p>
      {sub && <small>{sub}</small>}
    </div>
  )
}
