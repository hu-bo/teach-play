import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, FolderOpen, Trash2, Calendar } from 'lucide-react';
import { useProjects, useCreateProject, useDeleteProject } from '../hooks/useProjects';

export default function ProjectsPage() {
  const { data: projects, isLoading } = useProjects();
  const createProject = useCreateProject();
  const deleteProject = useDeleteProject();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectDesc, setNewProjectDesc] = useState('');

  const handleCreate = async () => {
    if (!newProjectName.trim()) return;

    try {
      await createProject.mutateAsync({
        name: newProjectName,
        description: newProjectDesc,
      });
      setShowCreateModal(false);
      setNewProjectName('');
      setNewProjectDesc('');
    } catch (error) {
      console.error('Create project failed:', error);
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (!confirm('确定要删除此项目吗？')) return;

    try {
      await deleteProject.mutateAsync(id);
    } catch (error) {
      console.error('Delete project failed:', error);
    }
  };

  return (
    <div className="p-6">
      {/* 头部 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">项目列表</h1>
          <p className="text-gray-500">管理你的自动化项目</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn btn-primary flex items-center gap-2"
        >
          <Plus size={20} />
          新建项目
        </button>
      </div>

      {/* 项目列表 */}
      {isLoading ? (
        <div className="text-center text-gray-500 py-12">加载中...</div>
      ) : projects?.length === 0 ? (
        <div className="text-center py-12">
          <FolderOpen size={48} className="mx-auto text-gray-300 mb-4" />
          <p className="text-gray-500">暂无项目</p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="mt-4 text-primary-600 hover:underline"
          >
            创建第一个项目
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects?.map((project) => (
            <Link
              key={project.id}
              to={`/projects/${project.id}`}
              className="card hover:shadow-lg transition-shadow group"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center">
                    <FolderOpen size={20} className="text-primary-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{project.name}</h3>
                    <p className="text-sm text-gray-500">
                      {project.recordings.length} 个录制
                    </p>
                  </div>
                </div>
                <button
                  onClick={(e) => handleDelete(project.id, e)}
                  className="p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-red-100 text-red-600 transition-opacity"
                >
                  <Trash2 size={16} />
                </button>
              </div>
              {project.description && (
                <p className="mt-3 text-sm text-gray-600 line-clamp-2">
                  {project.description}
                </p>
              )}
              <div className="mt-3 flex items-center gap-1 text-xs text-gray-400">
                <Calendar size={12} />
                {new Date(project.created_at).toLocaleDateString()}
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* 创建项目弹窗 */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-[400px] p-6">
            <h2 className="text-lg font-semibold mb-4">新建项目</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  项目名称
                </label>
                <input
                  type="text"
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  placeholder="输入项目名称..."
                  className="input"
                  autoFocus
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  项目描述
                </label>
                <textarea
                  value={newProjectDesc}
                  onChange={(e) => setNewProjectDesc(e.target.value)}
                  placeholder="输入项目描述..."
                  rows={3}
                  className="input resize-none"
                />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="btn btn-secondary"
              >
                取消
              </button>
              <button
                onClick={handleCreate}
                disabled={!newProjectName.trim() || createProject.isPending}
                className="btn btn-primary disabled:opacity-50"
              >
                {createProject.isPending ? '创建中...' : '创建'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
