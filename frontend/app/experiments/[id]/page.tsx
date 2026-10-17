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

const statusColors: Record<string, string> = {
  running: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  completed: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  failed: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  queued: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
}

export default async function ExperimentPage({ params }: { params: { id: string } }) {
  const experiment = await getExperiment(params.id)
  const runs = await getRuns(params.id)

  if (!experiment) {
    return <div className="p-8">Experiment not found</div>
  }

  return (
    <div className="min-h-screen p-8">
      <nav className="mb-6">
        <Link href={`/projects/${experiment.project_id}`} className="text-blue-600 hover:underline">
          ← Back to Project
        </Link>
      </nav>

      <header className="mb-8">
        <h1 className="text-3xl font-bold mb-2">{experiment.name}</h1>
        <p className="text-gray-500">{runs.length} runs</p>
      </header>

      <main className="max-w-6xl">
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
      </main>
    </div>
  )
}
