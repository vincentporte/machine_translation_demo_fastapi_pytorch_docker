@pytest.fixture(scope="module")
def verified_user() -> UserModel:
    return UserModel(
        email="verified@domain.com",
        hashed_password=atreides_password_hash,
        is_active=True,
        is_verified=True,
    )


@pytest.fixture(scope="module")
def unverified_user() -> UserModel:
    return UserModel(
        email="unverified@domain.com",
        hashed_password=atreides_password_hash,
        is_active=True,
        is_verified=False,
    )
