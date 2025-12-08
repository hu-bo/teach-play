import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import ProjectsPage from './pages/ProjectsPage';
import ProjectDetailPage from './pages/ProjectDetailPage';
import RecordingPage from './pages/RecordingPage';
import StepEditorPage from './pages/StepEditorPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<ProjectsPage />} />
          <Route path="projects/:projectId" element={<ProjectDetailPage />} />
          <Route path="recordings/:recordingId" element={<RecordingPage />} />
          <Route path="recordings/:recordingId/edit" element={<StepEditorPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
