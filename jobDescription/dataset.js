// Dataset from CSV file - Sample of candidate data
const csvDataset = [
  {
    "ID": "jasojo159",
    "Name": "Jason Jones",
    "Role": "E-commerce Specialist",
    "Resume": "Here's a professional resume for Jason Jones:\n\nJason Jones\nE-commerce Specialist\n\nContact Information:\n* Email: jasonjones@email.com\n* Phone: 555-123-4567\n* LinkedIn: linkedin.com/in/jasonjones\n\nSummary:\nResults-driven E-commerce Specialist with 5+ years of experience in inventory management, SEO, online advertising, and analytics. Proven track record of increasing online sales, improving website traffic, and optimizing inventory levels. Skilled in analyzing complex data sets, identifying trends, and making data-driven decisions.",
    "decision": "reject",
    "Reason_for_decision": "Lacked leadership skills for a senior position.",
    "Transcript": "Interviewer: Good morning, Jason. It's great to meet you. Welcome to the interview for the E-commerce Specialist role at our company.\n\nJason Jones: Good morning. Thank you for having me. It's a pleasure to be here.\n\nInterviewer: Can you start by telling me a little bit about your background and how you think your skills and experience make you a strong fit for this position?\n\nJason Jones: I have about 3 years of experience in e-commerce, working with online marketplaces like Amazon and eBay. My most recent role was as a customer service representative for an online retailer, where I handled customer inquiries, resolved issues, and provided product recommendations.",
    "Job_Description": "Be part of a passionate team at the forefront of machine learning as a E-commerce Specialist, delivering innovative solutions and driving business growth."
  },
  {
    "ID": "marsmith001",
    "Name": "Maria Smith",
    "Role": "Data Scientist",
    "Resume": "Maria Smith\nData Scientist\n\nContact Information:\n* Email: maria.smith@email.com\n* Phone: 555-987-6543\n* LinkedIn: linkedin.com/in/mariasmith\n\nEducation:\n* M.S. in Data Science, Stanford University (2019)\n* B.S. in Mathematics, UC Berkeley (2017)\n\nTechnical Skills:\n* Programming: Python, R, SQL, Java\n* Machine Learning: Scikit-learn, TensorFlow, PyTorch\n* Data Visualization: Matplotlib, Seaborn, Tableau\n* Big Data: Spark, Hadoop, Hive\n* Cloud Platforms: AWS, Google Cloud, Azure\n\nProfessional Experience:\nData Scientist, Tech Corp (2020-Present)\n* Developed predictive models that improved customer retention by 25%\n* Built recommendation systems serving 1M+ users daily\n* Led cross-functional teams to implement ML solutions",
    "decision": "select",
    "Reason_for_decision": "Strong technical background in machine learning and data science. Excellent problem-solving skills and proven track record of delivering impactful ML solutions. Perfect fit for our data science team.",
    "Transcript": "Interviewer: Thank you for joining us today, Maria. Can you walk us through your experience with machine learning?\n\nMaria Smith: Certainly. I've been working with ML for over 4 years, focusing on predictive modeling and recommendation systems. At my current role, I developed models that improved customer retention by 25%.\n\nInterviewer: That's impressive. Can you tell us about a challenging project you worked on?\n\nMaria Smith: One of the most challenging projects was building a real-time recommendation system. We had to handle millions of user interactions daily while maintaining low latency. I used collaborative filtering combined with deep learning approaches.",
    "Job_Description": "Join our data science team to develop cutting-edge machine learning solutions and drive data-driven decision making across the organization."
  },
  {
    "ID": "johndoe123",
    "Name": "John Doe",
    "Role": "Software Engineer",
    "Resume": "John Doe\nSoftware Engineer\n\nContact Information:\n* Email: john.doe@email.com\n* Phone: 555-456-7890\n* GitHub: github.com/johndoe\n* LinkedIn: linkedin.com/in/johndoe\n\nTechnical Skills:\n* Languages: JavaScript, Python, Java, TypeScript\n* Frontend: React, Vue.js, HTML5, CSS3\n* Backend: Node.js, Django, Spring Boot\n* Databases: PostgreSQL, MongoDB, Redis\n* Cloud: AWS, Docker, Kubernetes\n* Tools: Git, Jenkins, JIRA\n\nProfessional Experience:\nSoftware Engineer, StartupXYZ (2020-Present)\n* Built scalable web applications serving 100K+ users\n* Implemented microservices architecture reducing system downtime by 40%\n* Led frontend development team of 5 engineers",
    "decision": "select",
    "Reason_for_decision": "Excellent technical skills in full-stack development. Strong leadership experience and proven ability to build scalable systems. Great communication skills and cultural fit for our engineering team.",
    "Transcript": "Interviewer: Hi John, let's start by discussing your technical background and recent projects.\n\nJohn Doe: Sure! I've been working as a full-stack developer for 4 years, primarily using React and Node.js. Recently, I led the migration of our monolithic application to microservices, which reduced our system downtime by 40%.\n\nInterviewer: That's great. How do you approach system design for scalability?\n\nJohn Doe: I always start by understanding the requirements and expected load. Then I consider factors like data consistency, availability, and partition tolerance. For our recent project, we used event-driven architecture with message queues to handle high throughput.",
    "Job_Description": "Software Engineer position requiring full-stack development skills with focus on scalable web applications and modern technologies. Experience with React, Node.js, and cloud platforms preferred."
  },
  {
    "ID": "sarahwilson456",
    "Name": "Sarah Wilson",
    "Role": "Product Manager",
    "Resume": "Sarah Wilson\nProduct Manager\n\nContact Information:\n* Email: sarah.wilson@email.com\n* Phone: 555-789-0123\n* LinkedIn: linkedin.com/in/sarahwilson\n\nEducation:\n* MBA, Harvard Business School (2018)\n* B.S. in Computer Science, MIT (2016)\n\nProfessional Experience:\nSenior Product Manager, TechGiant Inc. (2019-Present)\n* Led product strategy for mobile app with 5M+ users\n* Increased user engagement by 35% through data-driven feature development\n* Managed cross-functional teams of 15+ engineers and designers\n* Launched 3 major product features resulting in $2M additional revenue\n\nProduct Manager, Innovation Labs (2018-2019)\n* Developed go-to-market strategy for AI-powered analytics platform\n* Conducted user research and competitive analysis\n* Collaborated with engineering teams to define technical requirements",
    "decision": "select",
    "Reason_for_decision": "Outstanding product management experience with proven track record of driving user growth and revenue. Strong technical background combined with business acumen. Excellent leadership and communication skills.",
    "Transcript": "Interviewer: Sarah, can you tell us about your approach to product strategy?\n\nSarah Wilson: I believe in data-driven product development. I start by understanding user needs through research and analytics, then prioritize features based on impact and feasibility. At my current role, this approach helped increase user engagement by 35%.\n\nInterviewer: How do you handle conflicting priorities from different stakeholders?\n\nSarah Wilson: Communication is key. I organize regular stakeholder meetings to align on goals and trade-offs. I use data to support decisions and ensure everyone understands the rationale behind prioritization choices.",
    "Job_Description": "Product Manager role focusing on mobile applications and user experience optimization. Requires strong analytical skills and experience with agile development processes."
  },
  {
    "ID": "mikebrown789",
    "Name": "Mike Brown",
    "Role": "Data Engineer",
    "Resume": "Mike Brown\nData Engineer\n\nContact Information:\n* Email: mike.brown@email.com\n* Phone: 555-234-5678\n* LinkedIn: linkedin.com/in/mikebrown\n\nTechnical Skills:\n* Programming: Python, Scala, Java, SQL\n* Big Data: Apache Spark, Hadoop, Kafka\n* Databases: PostgreSQL, Cassandra, MongoDB\n* Cloud: AWS (S3, EMR, Redshift), Google Cloud\n* Tools: Airflow, Docker, Kubernetes\n\nProfessional Experience:\nSenior Data Engineer, DataCorp (2019-Present)\n* Built data pipelines processing 10TB+ daily\n* Designed and implemented real-time streaming architecture\n* Reduced data processing time by 60% through optimization\n* Mentored junior engineers and established best practices",
    "decision": "reject",
    "Reason_for_decision": "While technically competent, lacks experience with our specific tech stack (Snowflake, dbt). Also showed limited knowledge of data governance and compliance requirements which are critical for our industry.",
    "Transcript": "Interviewer: Mike, can you describe your experience with data pipeline architecture?\n\nMike Brown: I've built numerous data pipelines using Apache Spark and Kafka. At my current role, I designed a system that processes over 10TB of data daily with sub-hour latency.\n\nInterviewer: How do you ensure data quality and governance?\n\nMike Brown: We use automated testing and monitoring. I implement data validation checks at each stage of the pipeline... though I haven't worked much with formal governance frameworks.\n\nInterviewer: What about compliance requirements like GDPR?\n\nMike Brown: That's handled more by our legal team. I focus mainly on the technical implementation.",
    "Job_Description": "Data Engineer position requiring expertise in cloud data platforms, data governance, and compliance. Experience with Snowflake, dbt, and regulatory requirements preferred."
  },
  {
    "ID": "emilydavis321",
    "Name": "Emily Davis",
    "Role": "UI Engineer",
    "Resume": "Emily Davis\nUI Engineer\n\nContact Information:\n* Email: emily.davis@email.com\n* Phone: 555-345-6789\n* Portfolio: emilydesigns.com\n* LinkedIn: linkedin.com/in/emilydavis\n\nTechnical Skills:\n* Frontend: React, Vue.js, Angular, TypeScript\n* Styling: CSS3, SASS, Styled Components\n* Design: Figma, Adobe Creative Suite\n* Testing: Jest, Cypress, React Testing Library\n* Tools: Webpack, Vite, Git\n\nProfessional Experience:\nSenior UI Engineer, DesignTech (2020-Present)\n* Led UI development for award-winning mobile application\n* Implemented design system used across 5+ products\n* Improved page load times by 45% through performance optimization\n* Collaborated closely with UX designers and product managers",
    "decision": "select",
    "Reason_for_decision": "Exceptional frontend development skills with strong design sensibility. Proven experience in building scalable UI components and design systems. Great portfolio demonstrating both technical and creative abilities.",
    "Transcript": "Interviewer: Emily, can you walk us through your approach to building reusable UI components?\n\nEmily Davis: I focus on creating components that are both flexible and consistent. I start by analyzing design patterns across the application, then build a component library with clear APIs and documentation. At my current role, our design system is used across 5 different products.\n\nInterviewer: How do you balance design aesthetics with performance?\n\nEmily Davis: Performance is crucial for user experience. I use techniques like code splitting, lazy loading, and optimized images. I also work closely with designers to ensure beautiful interfaces don't compromise speed - we achieved 45% faster load times in our recent redesign.",
    "Job_Description": "UI Engineer role focusing on React-based applications and design system development. Requires strong CSS skills and experience with modern frontend tooling."
  },
  {
    "ID": "davidlee654",
    "Name": "David Lee",
    "Role": "DevOps Engineer",
    "Resume": "David Lee\nDevOps Engineer\n\nContact Information:\n* Email: david.lee@email.com\n* Phone: 555-456-7890\n* LinkedIn: linkedin.com/in/davidlee\n\nTechnical Skills:\n* Cloud Platforms: AWS, Azure, Google Cloud\n* Containers: Docker, Kubernetes, Helm\n* Infrastructure: Terraform, CloudFormation\n* CI/CD: Jenkins, GitLab CI, GitHub Actions\n* Monitoring: Prometheus, Grafana, ELK Stack\n* Scripting: Python, Bash, PowerShell\n\nProfessional Experience:\nDevOps Engineer, CloudFirst Inc. (2019-Present)\n* Managed infrastructure for applications serving 1M+ users\n* Implemented CI/CD pipelines reducing deployment time by 70%\n* Automated infrastructure provisioning using Infrastructure as Code\n* Achieved 99.9% uptime through robust monitoring and alerting",
    "decision": "select",
    "Reason_for_decision": "Strong DevOps expertise with hands-on experience in cloud platforms and automation. Proven track record of improving deployment efficiency and system reliability. Good cultural fit and collaborative approach.",
    "Transcript": "Interviewer: David, how do you approach infrastructure automation?\n\nDavid Lee: I believe in Infrastructure as Code principles. I use Terraform for provisioning and Ansible for configuration management. This approach ensures consistency and makes our infrastructure reproducible and version-controlled.\n\nInterviewer: Can you describe a challenging incident you resolved?\n\nDavid Lee: We had a critical outage due to a database connection pool exhaustion. I quickly identified the issue through our monitoring dashboards, implemented a temporary fix, and then worked on a long-term solution involving connection pooling optimization and better resource limits.",
    "Job_Description": "DevOps Engineer position requiring expertise in cloud infrastructure, containerization, and CI/CD pipelines. Experience with Kubernetes and Infrastructure as Code tools essential."
  },
  {
    "ID": "lisachen987",
    "Name": "Lisa Chen",
    "Role": "Marketing Manager",
    "Resume": "Lisa Chen\nMarketing Manager\n\nContact Information:\n* Email: lisa.chen@email.com\n* Phone: 555-567-8901\n* LinkedIn: linkedin.com/in/lisachen\n\nEducation:\n* MBA in Marketing, Northwestern Kellogg (2018)\n* B.A. in Communications, UCLA (2016)\n\nProfessional Experience:\nMarketing Manager, GrowthCo (2020-Present)\n* Led digital marketing campaigns generating $5M+ in revenue\n* Increased brand awareness by 150% through integrated marketing strategy\n* Managed marketing budget of $2M across multiple channels\n* Built and led marketing team of 8 professionals\n\nDigital Marketing Specialist, StartupHub (2018-2020)\n* Developed content marketing strategy increasing organic traffic by 200%\n* Managed social media presence across 5 platforms\n* Implemented marketing automation workflows improving lead conversion by 40%",
    "decision": "reject",
    "Reason_for_decision": "Good marketing experience but lacks specific B2B SaaS experience which is crucial for our target market. Also showed limited understanding of technical product marketing and developer-focused go-to-market strategies.",
    "Transcript": "Interviewer: Lisa, can you tell us about your experience with B2B marketing?\n\nLisa Chen: Most of my experience has been in B2C marketing, but I believe the principles are transferable. I've worked on lead generation and conversion optimization.\n\nInterviewer: How would you approach marketing to developers and technical audiences?\n\nLisa Chen: I would focus on content marketing and thought leadership... though I haven't specifically marketed to developers before. I'd need to learn more about their preferences and channels.\n\nInterviewer: What's your experience with product marketing for technical products?\n\nLisa Chen: I've done some product marketing, but mostly for consumer products. Technical product marketing would be new for me.",
    "Job_Description": "Marketing Manager role focusing on B2B SaaS products and developer tools. Requires experience with technical product marketing and developer community engagement."
  },
  {
    "ID": "alexchen456",
    "Name": "Alex Chen",
    "Role": "Backend Engineer",
    "Resume": "Alex Chen\nBackend Engineer\n\nContact Information:\n* Email: alex.chen@email.com\n* Phone: 555-678-9012\n* GitHub: github.com/alexchen\n\nTechnical Skills:\n* Languages: Java, Python, Go, C++\n* Frameworks: Spring Boot, Django, FastAPI\n* Databases: MySQL, PostgreSQL, MongoDB, Redis\n* Cloud: AWS, Docker, Kubernetes\n* Message Queues: RabbitMQ, Apache Kafka\n\nProfessional Experience:\nSenior Backend Engineer, TechFlow Inc. (2019-Present)\n* Designed and implemented microservices architecture serving 500K+ requests/day\n* Optimized database queries reducing response time by 50%\n* Led API development team of 6 engineers",
    "decision": "select",
    "Reason_for_decision": "Excellent backend engineering skills with strong experience in microservices and high-scale systems. Proven leadership abilities and deep technical knowledge in our tech stack.",
    "Transcript": "Interviewer: Alex, can you describe your experience with microservices architecture?\n\nAlex Chen: I've been working with microservices for over 4 years. At my current role, I designed a system that handles 500K requests daily. We used Spring Boot with Docker and Kubernetes for orchestration.\n\nInterviewer: How do you handle data consistency across services?\n\nAlex Chen: We use event-driven architecture with Kafka for async communication, and implement the Saga pattern for distributed transactions. For critical operations, we use two-phase commit when necessary.",
    "Job_Description": "Backend Engineer position requiring expertise in microservices, high-scale systems, and cloud technologies. Java and Spring Boot experience essential."
  },
  {
    "ID": "rachelgreen789",
    "Name": "Rachel Green",
    "Role": "UX Designer",
    "Resume": "Rachel Green\nUX Designer\n\nContact Information:\n* Email: rachel.green@email.com\n* Phone: 555-789-0123\n* Portfolio: racheldesigns.com\n\nEducation:\n* M.A. in Human-Computer Interaction, Carnegie Mellon (2019)\n* B.A. in Psychology, Stanford University (2017)\n\nDesign Skills:\n* User Research & Testing\n* Wireframing & Prototyping\n* Design Systems\n* Tools: Figma, Sketch, Adobe Creative Suite\n* Analytics: Google Analytics, Hotjar\n\nProfessional Experience:\nSenior UX Designer, DesignLab (2020-Present)\n* Led UX research for mobile app with 2M+ users\n* Increased user engagement by 40% through redesign\n* Established design system used across 8 products",
    "decision": "select",
    "Reason_for_decision": "Outstanding UX design skills with strong research background. Proven track record of improving user engagement and establishing scalable design systems. Great portfolio and communication skills.",
    "Transcript": "Interviewer: Rachel, can you walk us through your design process?\n\nRachel Green: I always start with user research to understand pain points and needs. Then I create user personas and journey maps, followed by wireframes and prototypes. I validate designs through user testing before final implementation.\n\nInterviewer: How do you measure the success of your designs?\n\nRachel Green: I use both quantitative and qualitative metrics. For our recent mobile app redesign, we saw 40% increase in engagement and 25% reduction in support tickets. I also conduct regular user interviews to gather feedback.",
    "Job_Description": "UX Designer role focusing on mobile applications and user research. Requires strong portfolio and experience with design systems."
  },
  {
    "ID": "tomwilson321",
    "Name": "Tom Wilson",
    "Role": "Sales Manager",
    "Resume": "Tom Wilson\nSales Manager\n\nContact Information:\n* Email: tom.wilson@email.com\n* Phone: 555-890-1234\n* LinkedIn: linkedin.com/in/tomwilson\n\nEducation:\n* MBA in Sales & Marketing, Wharton (2018)\n* B.S. in Business Administration, UCLA (2016)\n\nProfessional Experience:\nSales Manager, SalesForce Pro (2019-Present)\n* Managed sales team of 12 representatives\n* Exceeded annual targets by 125% for 3 consecutive years\n* Generated $5M+ in new business revenue\n* Implemented CRM system improving team efficiency by 30%\n\nSales Representative, StartupSales (2018-2019)\n* Top performer with 150% of quota achievement\n* Developed key client relationships worth $2M+ annually",
    "decision": "reject",
    "Reason_for_decision": "Strong sales background but lacks experience in our specific industry (SaaS/Tech). Also showed limited understanding of technical product sales and developer-focused sales cycles.",
    "Transcript": "Interviewer: Tom, can you tell us about your experience selling to technical audiences?\n\nTom Wilson: Most of my experience has been in traditional B2B sales. I've sold to business decision makers, but not specifically to developers or technical teams.\n\nInterviewer: How would you approach selling developer tools?\n\nTom Wilson: I would focus on ROI and business benefits... though I'd need to learn more about the technical aspects and how developers evaluate tools.\n\nInterviewer: What's your experience with product-led growth strategies?\n\nTom Wilson: I'm not familiar with that approach. My background is more in traditional sales funnels and direct outreach.",
    "Job_Description": "Sales Manager role for developer tools and SaaS products. Requires experience with technical sales and product-led growth strategies."
  },
  {
    "ID": "jenniferwang654",
    "Name": "Jennifer Wang",
    "Role": "QA Engineer",
    "Resume": "Jennifer Wang\nQA Engineer\n\nContact Information:\n* Email: jennifer.wang@email.com\n* Phone: 555-901-2345\n\nTechnical Skills:\n* Test Automation: Selenium, Cypress, Jest\n* Programming: Python, JavaScript, Java\n* Testing Tools: JIRA, TestRail, Postman\n* CI/CD: Jenkins, GitHub Actions\n* Performance Testing: JMeter, LoadRunner\n\nProfessional Experience:\nSenior QA Engineer, QualityFirst (2018-Present)\n* Built automated test suites reducing manual testing by 70%\n* Implemented CI/CD testing pipelines\n* Led quality assurance for 5 major product releases",
    "decision": "select",
    "Reason_for_decision": "Strong QA automation skills and experience with modern testing frameworks. Proven ability to implement comprehensive testing strategies and improve development workflows.",
    "Transcript": "Interviewer: Jennifer, how do you approach test automation strategy?\n\nJennifer Wang: I follow the test pyramid approach - unit tests at the base, integration tests in the middle, and fewer E2E tests at the top. I've implemented this at my current company, reducing our manual testing effort by 70%.\n\nInterviewer: How do you handle flaky tests?\n\nJennifer Wang: I focus on making tests deterministic by using proper waits, test data isolation, and running tests in parallel safely. I also implement retry mechanisms for genuinely flaky external dependencies.",
    "Job_Description": "QA Engineer position requiring test automation expertise and experience with CI/CD pipelines. Selenium and JavaScript testing experience preferred."
  },
  {
    "ID": "kevinbrown987",
    "Name": "Kevin Brown",
    "Role": "Security Engineer",
    "Resume": "Kevin Brown\nSecurity Engineer\n\nContact Information:\n* Email: kevin.brown@email.com\n* Phone: 555-012-3456\n\nSecurity Skills:\n* Penetration Testing\n* Vulnerability Assessment\n* Security Architecture\n* Compliance: SOC2, GDPR, HIPAA\n* Tools: Nessus, Burp Suite, Metasploit\n* Cloud Security: AWS, Azure\n\nProfessional Experience:\nSecurity Engineer, SecureCloud Inc. (2019-Present)\n* Conducted security assessments for 50+ applications\n* Implemented zero-trust security architecture\n* Achieved SOC2 Type II compliance\n* Reduced security incidents by 80%",
    "decision": "select",
    "Reason_for_decision": "Excellent security engineering background with hands-on experience in penetration testing and compliance. Strong track record of implementing security best practices and reducing incidents.",
    "Transcript": "Interviewer: Kevin, can you describe your approach to application security?\n\nKevin Brown: I believe in security by design. I work closely with development teams to implement secure coding practices, conduct regular code reviews, and perform automated security scanning in CI/CD pipelines.\n\nInterviewer: How do you stay current with security threats?\n\nKevin Brown: I follow security research, participate in bug bounty programs, and attend conferences like Black Hat and DEF CON. I also maintain a home lab for testing new attack vectors and defense techniques.",
    "Job_Description": "Security Engineer role focusing on application security and cloud infrastructure. Requires experience with penetration testing and security compliance frameworks."
  },
  {
    "ID": "amandasmith123",
    "Name": "Amanda Smith",
    "Role": "Technical Writer",
    "Resume": "Amanda Smith\nTechnical Writer\n\nContact Information:\n* Email: amanda.smith@email.com\n* Phone: 555-123-4567\n\nWriting Skills:\n* API Documentation\n* User Guides & Tutorials\n* Technical Specifications\n* Content Strategy\n* Tools: GitBook, Confluence, Markdown\n\nProfessional Experience:\nSenior Technical Writer, DocuTech (2018-Present)\n* Created comprehensive API documentation for developer platform\n* Improved documentation user satisfaction by 60%\n* Established documentation standards and style guide\n* Collaborated with engineering teams on 20+ product launches",
    "decision": "reject",
    "Reason_for_decision": "Good technical writing skills but lacks experience with our specific domain (AI/ML documentation). Also showed limited understanding of developer workflows and technical depth required for our products.",
    "Transcript": "Interviewer: Amanda, how do you approach documenting complex technical concepts?\n\nAmanda Smith: I start by understanding the user's perspective and break down complex topics into digestible sections. I use examples and diagrams to illustrate concepts.\n\nInterviewer: Do you have experience documenting AI/ML APIs?\n\nAmanda Smith: Not specifically AI/ML, but I've documented various APIs. I'd need to learn more about machine learning concepts and terminology.\n\nInterviewer: How do you ensure documentation stays current with rapid product changes?\n\nAmanda Smith: I usually rely on developers to notify me of changes... I haven't worked in environments with very rapid iteration cycles.",
    "Job_Description": "Technical Writer role for AI/ML platform documentation. Requires experience with developer tools and ability to work in fast-paced environment."
  }
];

// Export for use in HTML
if (typeof window !== 'undefined') {
  window.csvDataset = csvDataset;
}
