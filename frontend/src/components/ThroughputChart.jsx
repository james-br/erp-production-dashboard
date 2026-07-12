import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

export default function ThroughputChart({ data }) {
  const ticks = data
    .filter((_, i) => i % 7 === 0)
    .map((d) => d.date);

  return (
    <div className="panel">
      <h2>Daily throughput — units completed, last 30 days</h2>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
          <CartesianGrid stroke="#2f3542" vertical={false} />
          <XAxis
            dataKey="date"
            ticks={ticks}
            tickFormatter={(d) => d.slice(5)}
            tick={{ fill: "#97a0ad", fontSize: 11, fontFamily: "IBM Plex Mono" }}
            axisLine={{ stroke: "#2f3542" }}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: "#97a0ad", fontSize: 11, fontFamily: "IBM Plex Mono" }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            cursor={{ fill: "rgba(255,106,19,0.08)" }}
            contentStyle={{
              background: "#232833",
              border: "1px solid #2f3542",
              borderRadius: 6,
              fontFamily: "IBM Plex Mono",
              fontSize: 12,
            }}
            labelStyle={{ color: "#97a0ad" }}
            itemStyle={{ color: "#e9ebef" }}
          />
          <Bar dataKey="units" fill="#ff6a13" radius={[2, 2, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
