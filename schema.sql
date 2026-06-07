CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firebase_uid    VARCHAR(128) UNIQUE NOT NULL,
    name            VARCHAR(100) NOT NULL,
    email           VARCHAR(255) UNIQUE NOT NULL,
    learning_style  VARCHAR(20) DEFAULT 'theory',
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE TABLE subjects (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title       VARCHAR(150) NOT NULL,
    color       VARCHAR(7) DEFAULT '#7F77DD',
    exam_date   DATE,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE TABLE resources (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_id       UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    type             VARCHAR(20) NOT NULL,
    title            VARCHAR(255) NOT NULL,
    raw_text         TEXT,
    summary          TEXT,
    flashcards_json  JSONB DEFAULT '[]',
    source_url       VARCHAR(2048),
    file_path        VARCHAR(1024),
    created_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE TABLE quizzes (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_id       UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    resource_id      UUID REFERENCES resources(id) ON DELETE SET NULL,
    difficulty       VARCHAR(10) DEFAULT 'medium',
    total_questions  INT NOT NULL DEFAULT 10,
    questions_json   JSONB NOT NULL DEFAULT '[]',
    created_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE TABLE quiz_attempts (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_id          UUID NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
    user_id          UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    score            INT NOT NULL DEFAULT 0,
    total            INT NOT NULL DEFAULT 0,
    answers_json     JSONB DEFAULT '{}',
    weak_topics_json JSONB DEFAULT '[]',
    attempted_at     TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE TABLE study_plans (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject_id  UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    start_date  DATE NOT NULL,
    end_date    DATE NOT NULL,
    plan_json   JSONB DEFAULT '{}',
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE TABLE plan_tasks (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id          UUID NOT NULL REFERENCES study_plans(id) ON DELETE CASCADE,
    title            VARCHAR(255) NOT NULL,
    scheduled_date   DATE NOT NULL,
    duration_mins    INT NOT NULL DEFAULT 30,
    completed        BOOLEAN DEFAULT FALSE,
    updated_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE TABLE chat_sessions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject_id  UUID REFERENCES subjects(id) ON DELETE SET NULL,
    title       VARCHAR(255) DEFAULT 'New chat',
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE TABLE chat_messages (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id   UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role         VARCHAR(10) NOT NULL,
    content      TEXT NOT NULL,
    sources_json JSONB DEFAULT '[]',
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE TABLE progress (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject_id      UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    study_minutes   INT DEFAULT 0,
    quiz_score      INT DEFAULT 0,
    streak_days     INT DEFAULT 0,
    recorded_date   DATE NOT NULL DEFAULT CURRENT_DATE,
    UNIQUE (user_id, subject_id, recorded_date)
);
CREATE INDEX idx_subjects_user         ON subjects(user_id);
CREATE INDEX idx_resources_subject     ON resources(subject_id);
CREATE INDEX idx_quizzes_subject       ON quizzes(subject_id);
CREATE INDEX idx_quiz_attempts_user    ON quiz_attempts(user_id);
CREATE INDEX idx_chat_messages_session ON chat_messages(session_id);
CREATE INDEX idx_progress_user_date    ON progress(user_id, recorded_date);
