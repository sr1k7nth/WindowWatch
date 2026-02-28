import { useEffect, useState } from "react";
import { Bar } from 'react-chartjs-2';


export default function Monthly() {
  type MonthlyData = {
    [date: string]: { [app: string]: number };
  };

  const [monthly, setMonthly] = useState<MonthlyData>({});
  const [totals, setTotals] = useState<Record<string, number>>({});
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");
  const numWeeks = Object.keys(monthly).length;

  async function fetchMonthly() {
    try {
      const [monthlyRes, statusRes] = await Promise.all([
        fetch("http://localhost:7777/api/monthly"),
        fetch("http://localhost:7777/api/status")
      ]);

      if (!monthlyRes.ok) {
        throw new Error("Monthly API failed");
      }

      if (!statusRes.ok) {
        throw new Error("Status API failed");
      }

      const weeklyData = await monthlyRes.json();
      const statusData = await statusRes.json();

      if (!statusData.running) {
        setStatus("Tracker stopped");
      } else if (statusData.error) {
        setStatus(`Tracker error: ${statusData.error}`);
      } else {
        setStatus("Running");
      }

      setMonthly(weeklyData.daily);
      setTotals(weeklyData.totals);
      setError("");
    }
    catch (err) {
      setError("Backend offline");
      setStatus("Offline");
      setMonthly({});
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
    fetchMonthly();
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

  const mainLabels = Object.keys(monthly);

  const sortedApps = Object.keys(totals);

  const datasets = sortedApps.map((app, index) => ({
    label: app,
    data: mainLabels.map(d => monthly[d]?.[app] || 0),
    borderColor: COLORS[index % COLORS.length],
    backgroundColor: COLORS[index % COLORS.length],
    tension: 0.3
  }));

  const chartData = { labels: mainLabels, datasets };

  const chartOptions = {
    plugins: {
      title: {
        display: true,
        text: 'Chart.js Bar Chart - Stacked',
      },
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
        stacked: true,
        grid: { display: false },
        ticks: { color: '#ffffff' },
      },
      y: {
        stacked: true,
        beginAtZero: true,
        grid: { color: 'rgba(255, 255, 255, 0.1)' },
        ticks: { color: '#ffffff' },
      },
    },
    barThickness: numWeeks <= 2 ? 120 : 70,
    maxBarThickness: 150,
    responsive: true,
  };

  if (!Object.keys(monthly).length) {
    return (
      <div className="text-center">
        <p className="text-yellow-500">{error || "No data available"}</p>
        <p className="text-yellow-500">{status}</p>
      </div>
    );
  }

  return (
    <>
      <div className="w-full bg-[#24273a] rounded-xl p-8 text-white">
        <h1 className="text-2xl mb-5 font-bold text-center">
          Monthly Time Stats
        </h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">

          <div className="relative w-full h-[400px] flex items-center justify-center">
            <div className="w-full h-full">
              <Bar data={chartData} options={chartOptions} />
            </div>
          </div>

          <div className="space-y-5">
            {Object.entries(totals).map(([app, time], index) => {
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
                        backgroundColor: COLORS[index % COLORS.length]
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>

        </div>
      </div>
    </>
  );
}