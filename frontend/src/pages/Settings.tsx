import { useState } from 'react'
import { useAuthStore } from '../store/authStore'
import { User, Lock, Bell, Database } from 'lucide-react'
import toast from 'react-hot-toast'

const Settings = () => {
  const { user } = useAuthStore()
  const [activeTab, setActiveTab] = useState('profile')

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Settings</h1>
        <p className="text-gray-400 mt-1">Manage your account and preferences</p>
      </div>

      <div className="flex gap-4 border-b border-dark-800">
        {[
          { id: 'profile', name: 'Profile', icon: User },
          { id: 'security', name: 'Security', icon: Lock },
          { id: 'notifications', name: 'Notifications', icon: Bell },
          { id: 'data', name: 'Data & API', icon: Database },
        ].map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-primary-500 text-primary-500'
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
            >
              <Icon size={18} />
              {tab.name}
            </button>
          )
        })}
      </div>

      {activeTab === 'profile' && (
        <div className="card">
          <h2 className="text-xl font-semibold text-white mb-6">Profile Settings</h2>
          <div className="space-y-4">
            <div className="input-group">
              <label className="label">Full Name</label>
              <input
                type="text"
                defaultValue={user?.full_name}
                className="w-full"
              />
            </div>

            <div className="input-group">
              <label className="label">Email</label>
              <input
                type="email"
                defaultValue={user?.email}
                className="w-full"
                disabled
              />
            </div>

            <div className="input-group">
              <label className="label">Role</label>
              <input
                type="text"
                defaultValue={user?.role}
                className="w-full"
                disabled
              />
            </div>

            <button onClick={() => toast.success('Profile updated')} className="btn-primary">
              Save Changes
            </button>
          </div>
        </div>
      )}

      {activeTab === 'security' && (
        <div className="card">
          <h2 className="text-xl font-semibold text-white mb-6">Security Settings</h2>
          <div className="space-y-4">
            <div className="input-group">
              <label className="label">Current Password</label>
              <input type="password" className="w-full" />
            </div>

            <div className="input-group">
              <label className="label">New Password</label>
              <input type="password" className="w-full" />
            </div>

            <div className="input-group">
              <label className="label">Confirm New Password</label>
              <input type="password" className="w-full" />
            </div>

            <button onClick={() => toast.success('Password updated')} className="btn-primary">
              Update Password
            </button>
          </div>
        </div>
      )}

      {activeTab === 'notifications' && (
        <div className="card">
          <h2 className="text-xl font-semibold text-white mb-6">Notification Preferences</h2>
          <div className="space-y-4">
            {[
              { id: 'email', name: 'Email Notifications', description: 'Receive updates via email' },
              { id: 'compliance', name: 'Compliance Alerts', description: 'Get notified of compliance violations' },
              { id: 'performance', name: 'Performance Reports', description: 'Weekly performance summaries' },
              { id: 'ai', name: 'AI Insights', description: 'Receive AI-generated recommendations' },
            ].map((setting) => (
              <div key={setting.id} className="flex items-center justify-between p-4 bg-dark-800 rounded-lg">
                <div>
                  <p className="font-medium text-white">{setting.name}</p>
                  <p className="text-sm text-gray-400">{setting.description}</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" className="sr-only peer" defaultChecked />
                  <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'data' && (
        <div className="card">
          <h2 className="text-xl font-semibold text-white mb-6">Data & API Settings</h2>
          <div className="space-y-6">
            <div>
              <h3 className="font-medium text-white mb-2">API Keys</h3>
              <div className="space-y-3">
                <div className="bg-dark-800 p-4 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-400">Polygon API Key</span>
                    <button className="text-sm text-primary-500 hover:text-primary-400">Update</button>
                  </div>
                  <code className="text-xs text-gray-500 font-mono">••••••••••••••••••••</code>
                </div>

                <div className="bg-dark-800 p-4 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-400">Alpha Vantage API Key</span>
                    <button className="text-sm text-primary-500 hover:text-primary-400">Update</button>
                  </div>
                  <code className="text-xs text-gray-500 font-mono">••••••••••••••••••••</code>
                </div>
              </div>
            </div>

            <div>
              <h3 className="font-medium text-white mb-2">Data Refresh</h3>
              <button onClick={() => toast.success('Data refresh initiated')} className="btn-secondary">
                Refresh All Data
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Settings
