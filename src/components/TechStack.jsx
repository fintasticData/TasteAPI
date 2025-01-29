import React from 'react';
import './styles/TechStack.css';

const TechStack = () => {
  const techStack = [
    {
      title: 'Version Control & Collaboration',
      items: ['Git (GitHub/GitLab/Bitbucket)'],
    },
    {
      title: 'DevOps & Infrastructure',
      items: ['Docker', 'Kubernetes', 'CI/CD Tools (GitHub Actions, Jenkins)'],
    },
    {
      title: 'Database & Backend Services',
      items: ['Supabase'],
    },
    {
      title: 'Frontend Development',
      items: ['React', 'State Management (Redux/Recoil)', 'UI Libraries (Material-UI, Tailwind CSS)'],
    },
    {
      title: 'Backend Development',
      items: ['Python', 'FastAPI', 'Celery'],
    },
    {
      title: 'Machine Learning & AI',
      items: ['scikit-learn', 'TensorFlow', 'AI-Powered Insights'],
    },
    {
      title: 'Analytics & Data Processing',
      items: ['Pandas/Numpy', 'Recharts', 'Apache Kafka'],
    },
    {
      title: 'User Interaction & Experience',
      items: ['Framer Motion', 'Task Management'],
    },
    {
      title: 'Deployment & Monitoring',
      items: ['AWS', 'Prometheus', 'Grafana'],
    },
    {
      title: 'Security & Compliance',
      items: ['Supabase Auth', 'GDPR Compliance'],
    },
  ];

  return (
    <section className="tech-stack">
      <h2>Tech Stack Roadmap</h2>
      <div className="tech-branches">
        {techStack.map((branch, index) => (
          <div key={index} className="tech-branch">
            <h3>{branch.title}</h3>
            <ul>
              {branch.items.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </section>
  );
};

export default TechStack;
