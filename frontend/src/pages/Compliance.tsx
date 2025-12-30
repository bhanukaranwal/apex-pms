import { useQuery } from 'react-query'
import { complianceAPI } from '../lib/api'
import { Shield, AlertTriangle, CheckCircle, XCircle } from 'lucide-react'

const Compliance = () => {
  const { data: rules } = useQuery('compliance-rules', () => complianceAPI.rules())
  const { data: violations } = useQuery('compliance-violations', () => complianceAPI.violations())

  const activeViolations = violations?.data?.filter((v: any) => !v.resolved) || []
  const resolvedViolations = violations?.data?.filter((v: any) => v.resolved) || []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Compliance</h1>
          <p className="text-gray-400 mt-1">Monitor regulatory compliance and violations</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-primary-600 p-2 rounded-lg">
              <Shield size={20} className="text-white" />
            </div>
            <div className="stat-label">Active Rules</div>
          </div>
          <div className="stat-value">{rules?.data?.filter((r: any) => r.is_active).length || 0}</div>
        </div>

        <div className="card">
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-red-600 p-2 rounded-lg">
              <AlertTriangle size={20} className="text-white" />
            </div>
            <div className="stat-label">Open Violations</div>
          </div>
          <div className="stat-value">{activeViolations.length}</div>
        </div>

        <div className="card">
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-green-600 p-2 rounded-lg">
              <CheckCircle size={20} className="text-white" />
            </div>
            <div className="stat-label">Resolved</div>
          </div>
          <div className="stat-value">{resolvedViolations.length}</div>
        </div>

        <div className="card">
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-yellow-600 p-2 rounded-lg">
              <XCircle size={20} className="text-white" />
            </div>
            <div className="stat-label">Compliance Score</div>
          </div>
          <div className="stat-value">92%</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-semibold text-white mb-4">Active Compliance Rules</h2>
          <div className="space-y-3">
            {rules?.data?.filter((r: any) => r.is_active).map((rule: any) => (
              <div key={rule.id} className="bg-dark-800 p-4 rounded-lg">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-white">{rule.name}</h3>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    rule.severity === 'critical' ? 'bg-red-900 text-red-300' :
                    rule.severity === 'error' ? 'bg-orange-900 text-orange-300' :
                    rule.severity === 'warning' ? 'bg-yellow-900 text-yellow-300' :
                    'bg-blue-900 text-blue-300'
                  }`}>
                    {rule.severity}
                  </span>
                </div>
                <p className="text-sm text-gray-400">{rule.description}</p>
                <div className="mt-2 text-xs text-gray-500">Type: {rule.rule_type}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold text-white mb-4">Recent Violations</h2>
          <div className="space-y-3">
            {activeViolations.slice(0, 5).map((violation: any) => (
              <div key={violation.id} className="bg-red-900 bg-opacity-20 border border-red-800 p-4 rounded-lg">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <AlertTriangle size={16} className="text-red-400" />
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      violation.severity === 'critical' ? 'bg-red-900 text-red-300' :
                      violation.severity === 'error' ? 'bg-orange-900 text-orange-300' :
                      'bg-yellow-900 text-yellow-300'
                    }`}>
                      {violation.severity}
                    </span>
                  </div>
                  <span className="text-xs text-gray-400">
                    {new Date(violation.violation_date).toLocaleDateString()}
                  </span>
                </div>
                <p className="text-sm text-gray-300">{violation.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="text-xl font-semibold text-white mb-4">All Violations</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="border-b border-dark-800">
              <tr>
                <th className="text-left py-3 px-2 text-sm font-medium text-gray-400">ID</th>
                <th className="text-left py-3 px-2 text-sm font-medium text-gray-400">Date</th>
                <th className="text-left py-3 px-2 text-sm font-medium text-gray-400">Severity</th>
                <th className="text-left py-3 px-2 text-sm font-medium text-gray-400">Description</th>
                <th className="text-left py-3 px-2 text-sm font-medium text-gray-400">Status</th>
              </tr>
            </thead>
            <tbody>
              {violations?.data?.map((violation: any) => (
                <tr key={violation.id} className="border-b border-dark-800 hover:bg-dark-800">
                  <td className="py-3 px-2 text-gray-400">#{violation.id}</td>
                  <td className="py-3 px-2 text-gray-300">
                    {new Date(violation.violation_date).toLocaleDateString()}
                  </td>
                  <td className="py-3 px-2">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      violation.severity === 'critical' ? 'bg-red-900 text-red-300' :
                      violation.severity === 'error' ? 'bg-orange-900 text-orange-300' :
                      'bg-yellow-900 text-yellow-300'
                    }`}>
                      {violation.severity}
                    </span>
                  </td>
                  <td className="py-3 px-2 text-gray-300">{violation.description}</td>
                  <td className="py-3 px-2">
                    {violation.resolved ? (
                      <span className="px-2 py-1 rounded text-xs font-medium bg-green-900 text-green-300 flex items-center gap-1 w-fit">
                        <CheckCircle size={14} />
                        Resolved
                      </span>
                    ) : (
                      <span className="px-2 py-1 rounded text-xs font-medium bg-red-900 text-red-300 flex items-center gap-1 w-fit">
                        <XCircle size={14} />
                        Open
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Compliance
