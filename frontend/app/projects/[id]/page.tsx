import Link from 'next/link'

async function getProject(id: string) {
  const res = await fetch(`http://localhost:8001/api/projects/${id}`, { cache: 'no-store' })
  if (!res.ok) return null
  return res.json()
}

async function getExperiments(projectId: string) {
  const res = await fetch(`http://localhost:8001/api/experiments?project_id=${projectId}`, { cache: 'no-store' })
  if (!res.ok) return []
  return res.json()
}

export default async function ProjectPage({ params }: { params: { id: string } }) {
  const project = await getProject(params.id)
  const experiments = await getExperiments(params.id)

  if (!project) {
    return <div className="p-8">Project not found</div>
  }

  return (
    <div className="min-h-screen p-8">
      <nav className="mb-6">
        <Link href="/" className="text-blue-600 hover:underline">← Back to Projects</Link>
      </nav>

      <header className="mb-8">
        <h1 className="text-3xl font-bold mb-2">{project.name}</h1>
        {project.description && (
          <p className="text-gray-600 dark:text-gray-400">{project.description}</p>
        )}
      </header>

      <main className="max-w-6xl">
        <h2 className="text-2xl font-semibold mb-6">Experiments</h2>

        {experiments.length === 0 ? (
          <div className="border border-dashed border-gray-300 dark:border-gray-700 rounded-lg p-12 text-center">
            <p className="text-gray-500">No experiments yet</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {experiments.map((exp: any) => (
              <Link
                key={exp.id}
                href={`/experiments/${exp.id}`}
                className="block p-6 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-500"
              >
                <h3 className="text-xl font-semibold">{exp.name}</h3>
                <p className="text-sm text-gray-400 mt-2">
                  Created {new Date(exp.created_at).toLocaleDateString()}
                </p>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
