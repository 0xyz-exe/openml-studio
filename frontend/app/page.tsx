import Link from 'next/link'

async function getProjects() {
  const res = await fetch('http://localhost:8000/api/projects', { cache: 'no-store' })
  if (!res.ok) return []
  return res.json()
}

export default async function Home() {
  const projects = await getProjects()

  return (
    <div className="min-h-screen p-8">
      <header className="mb-8">
        <h1 className="text-4xl font-bold mb-2">OpenML Studio</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Framework-agnostic ML experiment tracking
        </p>
      </header>

      <main className="max-w-6xl">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-semibold">Projects</h2>
          <Link
            href="/projects/new"
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            New Project
          </Link>
        </div>

        {projects.length === 0 ? (
          <div className="border border-dashed border-gray-300 dark:border-gray-700 rounded-lg p-12 text-center">
            <p className="text-gray-500 mb-4">No projects yet</p>
            <p className="text-sm text-gray-400">
              Run the quick start example or create a project manually
            </p>
            <pre className="mt-4 text-xs bg-gray-100 dark:bg-gray-800 p-3 rounded inline-block text-left">
              python examples/quick_start.py
            </pre>
          </div>
        ) : (
          <div className="grid gap-4">
            {projects.map((project: any) => (
              <Link
                key={project.id}
                href={`/projects/${project.id}`}
                className="block p-6 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-500 dark:hover:border-blue-400"
              >
                <h3 className="text-xl font-semibold mb-2">{project.name}</h3>
                {project.description && (
                  <p className="text-gray-600 dark:text-gray-400">
                    {project.description}
                  </p>
                )}
                <p className="text-sm text-gray-400 mt-2">
                  Created {new Date(project.created_at).toLocaleDateString()}
                </p>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
