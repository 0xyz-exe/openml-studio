import Link from 'next/link'

async function getExperiment(id: string) {
  const res = await fetch(`http://localhost:8001/api/experiments/${id}`, { cache: 'no-store' })
  if (!res.ok) return null
  return res.json()
}

async function getRuns(experimentId: string) {
  const res = await fetch(`http://localhost:8001/api/runs?experiment_id=${experimentId}`, { cache: 'no-store' })
  if (!res.ok) return []
  return res.json()
}

async function getComparison(runIds: string[]) {
  if (runIds.length === 0) return { runs: [] }
  try {
    const res = await fetch(`http://localhost:8001/api/runs/compare?run_ids=${runIds.join(',')}`, { cache: 'no-store' })
    if (!res.ok) return { runs: [] }
    return res.json()
  } catch {
    return { runs: [] }
  }
}

const statusColors: Record<string, string> = {
  running: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  completed: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  failed: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  queued: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
}

export default async function ExperimentPage({ params }: { params: { id: string } }) {
  const experiment = await getExperiment(params.id)
  const runs = await getRuns(params.id)
  const comparison = runs.length > 1 ? await getComparison(runs.slice(0, 3).map((r: any) => r.id)) : null

  if (!experiment) {
    return <div className="p-8">Experiment not found</div>
  }

  const compRuns: any[] = comparison?.runs || []
  const allParamKeys = Array.from(new Set(compRuns.flatMap(r => Object.keys(r.params || {}))))
  const allMetricKeys = Array.from(new Set(compRuns.flatMap(r => Object.keys(r.metrics || {}))))

  return (
    <div className="min-h-screen p-8 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      <nav className="mb-6">
        <Link href={`/projects/${experiment.project_id}`} className="text-blue-600 hover:underline text-sm font-medium">
          ← Back to Project
        </Link>
      </nav>

      <header className="mb-8 flex justify-between items-end">
        <div>
          <span className="text-xs font-semibold tracking-wider text-blue-600 uppercase">Experiment</span>
          <h1 className="text-3xl font-bold mt-1">{experiment.name}</h1>
          <p className="text-gray-500 mt-1">{runs.length} logged training runs</p>
        </div>
      </header>

      <main className="max-w-6xl space-y-10">
        {/* Run Comparison Section */}
        {compRuns.length > 1 && (
          <section id="comparison" className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6 shadow-sm">
            <div className="flex justify-between items-center mb-4">
              <div>
                <h2 className="text-xl font-bold">Run Comparison &amp; Metrics</h2>
                <p className="text-sm text-gray-500">Side-by-side evaluation of training parameters and final validation metrics</p>
              </div>
              <span className="px-3 py-1 bg-blue-50 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300 text-xs font-semibold rounded-full border border-blue-200 dark:border-blue-700">
                {compRuns.length} Runs Compared
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b dark:border-gray-700 text-left bg-gray-50 dark:bg-gray-700/50">
                    <th className="px-4 py-3 font-semibold text-gray-600 dark:text-gray-300 w-1/4">Property</th>
                    {compRuns.map((r) => (
                      <th key={r.run_id} className="px-4 py-3 font-semibold text-gray-900 dark:text-white">
                        <Link href={`/runs/${r.run_id}`} className="text-blue-600 hover:underline">
                          {r.name || r.run_id.slice(0, 8)}
                        </Link>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                  <tr>
                    <td className="px-4 py-2.5 font-medium text-gray-500">Status</td>
                    {compRuns.map((r) => (
                      <td key={r.run_id} className="px-4 py-2.5">
                        <span className={`px-2 py-0.5 text-xs font-semibold rounded-full ${statusColors[r.status] || 'bg-gray-100'}`}>
                          {r.status}
                        </span>
                      </td>
                    ))}
                  </tr>

                  {allMetricKeys.length > 0 && (
                    <tr className="bg-gray-50/50 dark:bg-gray-800/80 font-semibold text-xs text-gray-500 uppercase tracking-wider">
                      <td colSpan={compRuns.length + 1} className="px-4 py-2">Validation Metrics</td>
                    </tr>
                  )}
                  {allMetricKeys.map((mKey) => (
                    <tr key={mKey} className="hover:bg-gray-50 dark:hover:bg-gray-700/30">
                      <td className="px-4 py-2.5 font-medium text-gray-700 dark:text-gray-300 capitalize">{mKey.replace('_', ' ')}</td>
                      {compRuns.map((r) => (
                        <td key={r.run_id} className="px-4 py-2.5 font-mono text-gray-900 dark:text-gray-100 font-semibold">
                          {r.metrics[mKey] !== undefined ? (typeof r.metrics[mKey] === 'number' ? r.metrics[mKey].toFixed(4) : r.metrics[mKey]) : '—'}
                        </td>
                      ))}
                    </tr>
                  ))}

                  {allParamKeys.length > 0 && (
                    <tr className="bg-gray-50/50 dark:bg-gray-800/80 font-semibold text-xs text-gray-500 uppercase tracking-wider">
                      <td colSpan={compRuns.length + 1} className="px-4 py-2">Hyperparameters</td>
                    </tr>
                  )}
                  {allParamKeys.map((pKey) => (
                    <tr key={pKey} className="hover:bg-gray-50 dark:hover:bg-gray-700/30">
                      <td className="px-4 py-2.5 font-medium text-gray-500 capitalize">{pKey.replace('_', ' ')}</td>
                      {compRuns.map((r) => (
                        <td key={r.run_id} className="px-4 py-2.5 font-mono text-xs text-gray-700 dark:text-gray-300">
                          {r.params[pKey] !== undefined ? String(r.params[pKey]) : '—'}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}

        <section id="run-history">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">Training Hyperparameters &amp; Run History</h2>
            <span className="text-sm text-gray-500">{runs.length} runs recorded</span>
          </div>
        {runs.length === 0 ? (
          <div className="border border-dashed border-gray-300 dark:border-gray-700 rounded-lg p-12 text-center">
            <p className="text-gray-500">No runs yet</p>
          </div>
        ) : (
          <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-800 border-b dark:border-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Run
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Started
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Parameters
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {runs.map((run: any) => (
                  <tr key={run.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                    <td className="px-6 py-4">
                      <Link href={`/runs/${run.id}`} className="text-blue-600 hover:underline font-medium">
                        {run.name || run.id.slice(0, 8)}
                      </Link>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${statusColors[run.status]}`}>
                        {run.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {new Date(run.start_time).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {Object.keys(run.params).length} params
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        </section>
      </main>
    </div>
  )
}
