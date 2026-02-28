import { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

export default function Weekly() {
  type WeeklyData = {
    [date: string]: { [app: string]: number };
  };

  const [weekly, setWeekly] = useState<WeeklyData>({});
  const [totals, setTotals] = useState<Record<string, number>>({});
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");

  async function fetchWeekly() {
    try {
      const [weeklyRes, statusRes] = await Promise.all([
        fetch("http://localhost:7777/api/weekly"),
        fetch("http://localhost:7777/api/status")
      ]);

      if (!weeklyRes.ok) {
        throw new Error("Weekly API failed");
      }

      if (!statusRes.ok) {
        throw new Error("Status API failed");
      }

      const weeklyData = await weeklyRes.json();
      const statusData = await statusRes.json();

      if (!statusData.running) {
        setStatus("Tracker stopped");
      } else if (statusData.error) {
        setStatus(`Tracker error: ${statusData.error}`);
      } else {
        setStatus("Running");
      }

      setWeekly(weeklyData.daily);
      setTotals(weeklyData.totals);
      setError("");
    }
    catch (err) {
      setError("Backend offline");
      setStatus("Offline");
      setWeekly({});
    }
  }

  const totalSeconds = Object.values(totals).reduce((acc, cur) => acc + cur, 0);

  function format_time(time: number) {
    const h = Math.floor(time / 3600);
    const m = Math.floor((time % 3600) / 60);
    const s = Math.floor(time % 60);
    return `${h > 0 ? h + 'h ' : ''}${m}m ${s}s`;
  }

  useEffect(() => {
    fetchWeekly();
  }, []);

  const COLORS = [
    'rgba(255, 99, 132, 1)',
    'rgba(54, 162, 235, 1)',
    'rgba(255, 206, 86, 1)',
    'rgba(75, 192, 192, 1)',
    'rgba(153, 102, 255, 1)',
    'rgba(255, 159, 64, 1)',
    'rgba(199, 56, 86, 1)',
    'rgba(36, 96, 168, 1)',
    'rgba(233, 182, 60, 1)',
    'rgba(47, 140, 140, 1)',
    'rgba(124, 75, 215, 1)',
    'rgba(217, 124, 50, 1)',
    'rgba(90, 200, 120, 1)',
    'rgba(200, 90, 200, 1)',
    'rgba(110, 110, 110, 1)',
  ];


  const dates = Object.keys(weekly);
  const apps = new Set<string>();

  dates.forEach(d => {
    Object.keys(weekly[d] || {}).forEach(app => apps.add(app))
  })

  const datasets = Array.from(apps).map((app, index) => ({
    label: app,
    data: dates.map(d => weekly[d]?.[app] || 0),
    borderColor: COLORS[index % COLORS.length],
    backgroundColor: COLORS[index % COLORS.length].replace("1)", "0.3)"),
    tension: 0.3
  }))

  const chartData = { labels: dates, datasets };

  const chartOptions = {
    plugins: {
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const value = context.raw;
            return ` Time: ${format_time(value)}`;
          }
        }
      },
      legend: {
        labels: {
          color: '#ffffff',
          font: { size: 17, }
        }
      }
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { color: '#ffffff' },
      },
      y: {
        grid: { color: 'rgba(255, 255, 255, 0.1)' },
        ticks: { color: '#ffffff' },
      },
    },
  }

  if (!dates.length) {
    return <div className="text-center">
      <p className="text-yellow-500">{error || "No data available"}</p>
      <p className="text-yellow-500">{status}</p>
    </div>;
  }

  return (
    <div className="w-full bg-[#24273a] rounded-xl p-8 text-white">
      <h1 className="text-2xl mb-5 font-bold text-center">
        Monthly Time Stats
      </h1>
      {error && <p className="text-red-400 mb-4 text-center">{error}</p>}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">

        <div className="relative w-full h-[400px] flex items-center justify-center">
          <div className="w-full h-full">
            <Line data={chartData} options={chartOptions} />
          </div>
        </div>

        <div className="space-y-5">
          {Object.entries(totals)
            .map(([app, time], index) => {
              const percent =
                totalSeconds > 0
                  ? (time / totalSeconds) * 100
                  : 0;

              return (
                <div key={app}>
                  <div className="flex justify-between mb-1 text-sm">
                    <span>{app}</span>
                    <span>{format_time(time)}</span>
                  </div>

                  <div className="w-full h-2 bg-[#11111b] rounded">
                    <div
                      className="h-2 rounded"
                      style={{
                        width: `${percent}%`,
                        backgroundColor:
                          COLORS[index % COLORS.length]
                      }}
                    />
                  </div>
                </div>
              );
            })}
        </div>
      </div>
    </div>
  );
}
