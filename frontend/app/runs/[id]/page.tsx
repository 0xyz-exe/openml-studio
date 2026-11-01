import Link from 'next/link'
import MetricChart from '@/components/MetricChart'

async function getRun(id: string) {
  const res = await fetch(`http://localhost:8001/api/runs/${id}`, { cache: 'no-store' })
  if (!res.ok) return null
  return res.json()
}

async function getMetrics(id: string) {
  const res = await fetch(`http://localhost:8001/api/runs/${id}/metrics`, { cache: 'no-store' })
  if (!res.ok) return []
  return res.json()
}

async function getArtifacts(id: string) {
  const res = await fetch(`http://localhost:8001/api/artifacts/${id}`, { cache: 'no-store' })
  if (!res.ok) return []
  return res.json()
}

export default async function RunPage({ params }: { params: { id: string } }) {
  const run = await getRun(params.id)
  const metrics = await getMetrics(params.id)
  const artifacts = await getArtifacts(params.id)

  if (!run) {
    return <div className="p-8">Run not found</div>
  }

  // Get unique metric names
  const metricNames: string[] = Array.from(new Set<string>(metrics.map((m: any) => m.name)))
  
  // Calculate final metrics (last step value)
  const finalMetrics: Record<string, number> = {}
  metricNames.forEach(name => {
    const metricValues = metrics.filter((m: any) => m.name === name).sort((a: any, b: any) => b.step - a.step)
    if (metricValues.length > 0) {
      finalMetrics[name] = metricValues[0].value
    }
  })

  return (
    <div className="min-h-screen p-8">
      <nav className="mb-6">
        <Link href={`/experiments/${run.experiment_id}`} className="text-blue-600 hover:underline">
          ← Back to Experiment
        </Link>
      </nav>

      <header className="mb-8">
        <h1 className="text-3xl font-bold mb-2">{run.name || 'Run ' + run.id.slice(0, 8)}</h1>
        <div className="flex gap-4 text-sm text-gray-500">
          <span>Status: <span className="font-semibold">{run.status}</span></span>
          <span>Started: {new Date(run.start_time).toLocaleString()}</span>
          {run.end_time && <span>Ended: {new Date(run.end_time).toLocaleString()}</span>}
        </div>
      </header>

      <main className="max-w-6xl space-y-8">
        {/* Metadata */}
        <section>
          <h2 className="text-2xl font-semibold mb-4">Metadata</h2>
          <div className="grid grid-cols-2 gap-4 bg-gray-50 dark:bg-gray-800 p-6 rounded-lg">
            {run.source_commit && (
              <div>
                <span className="text-sm text-gray-500">Source Commit</span>
                <p className="font-mono text-sm">{run.source_commit}</p>
              </div>
            )}
            {run.dataset_name && (
              <div>
                <span className="text-sm text-gray-500">Dataset</span>
                <p>{run.dataset_name} {run.dataset_version && `(v${run.dataset_version})`}</p>
              </div>
            )}
          </div>
        </section>

        {/* Parameters */}
        <section>
          <h2 className="text-2xl font-semibold mb-4">Parameters</h2>
          <div className="bg-gray-50 dark:bg-gray-800 p-6 rounded-lg">
            <pre className="text-sm overflow-x-auto">
              {JSON.stringify(run.params, null, 2)}
            </pre>
          </div>
        </section>

        {/* Final Metrics */}
        {Object.keys(finalMetrics).length > 0 && (
          <section>
            <h2 className="text-2xl font-semibold mb-4">Final Metrics</h2>
            <div className="grid grid-cols-3 gap-4">
              {Object.entries(finalMetrics).map(([name, value]) => (
                <div key={name} className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                  <p className="text-sm text-gray-500 mb-1">{name}</p>
                  <p className="text-2xl font-bold">{typeof value === 'number' ? value.toFixed(4) : value}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Metric Charts */}
        {metricNames.length > 0 && (
          <section id="metric-charts">
            <h2 className="text-2xl font-semibold mb-4">Metrics Over Time</h2>
            <div className="grid grid-cols-2 gap-4">
              {metricNames.map(name => (
                <MetricChart key={name} metrics={metrics} metricName={name} />
              ))}
            </div>
          </section>
        )}

        {/* Artifacts */}
        {artifacts.length > 0 && (
          <section id="artifacts">
            <h2 className="text-2xl font-semibold mb-4">Artifacts</h2>
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-50 dark:bg-gray-800 border-b dark:border-gray-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Filename</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Size</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {artifacts.map((artifact: any) => (
                    <tr key={artifact.id}>
                      <td className="px-6 py-4 text-sm">{artifact.filename}</td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {artifact.size_bytes ? (artifact.size_bytes / 1024).toFixed(1) + ' KB' : '-'}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {new Date(artifact.created_at).toLocaleString()}
                      </td>
                      <td className="px-6 py-4">
                        <a
                          href={`http://localhost:8001/api/artifacts/download/${artifact.id}`}
                          className="text-blue-600 hover:underline text-sm"
                          download
                        >
                          Download
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </main>
    </div>
  )
}
