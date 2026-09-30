CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(100),
    display_name VARCHAR(100),
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE ai_chat_usage (
    user_id BIGINT NOT NULL,
    usage_date DATE NOT NULL,
    chat_count INTEGER NOT NULL DEFAULT 0,

    PRIMARY KEY (user_id, usage_date),

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);


CREATE TABLE ai_chat_messages (
    id BIGSERIAL PRIMARY KEY,

    user_id BIGINT NOT NULL,

    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,

    model VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);


CREATE TABLE quiz_attempts (
    id BIGSERIAL PRIMARY KEY,

    user_id BIGINT NOT NULL,

    course VARCHAR(100) NOT NULL,
    topic VARCHAR(100) NOT NULL,

    score INTEGER NOT NULL,
    total_items INTEGER NOT NULL,

    percentage NUMERIC(5,2) NOT NULL,

    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);


CREATE TABLE quiz_answers (
    id BIGSERIAL PRIMARY KEY,

    attempt_id BIGINT NOT NULL,

    question_id VARCHAR(100) NOT NULL,

    selected_answer TEXT,
    correct_answer TEXT,

    is_correct BOOLEAN NOT NULL,

    FOREIGN KEY (attempt_id)
        REFERENCES quiz_attempts(id)
        ON DELETE CASCADE
);


CREATE INDEX idx_ai_chat_messages_user
ON ai_chat_messages(user_id);

CREATE INDEX idx_ai_chat_messages_created
ON ai_chat_messages(created_at);

CREATE INDEX idx_quiz_attempts_user
ON quiz_attempts(user_id);

CREATE INDEX idx_quiz_attempts_course_topic
ON quiz_attempts(course, topic);

CREATE INDEX idx_quiz_attempts_completed
ON quiz_attempts(completed_at);