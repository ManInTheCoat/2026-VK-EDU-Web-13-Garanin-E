def sidebar_data(request):
  popular_tags = [
    {'name': 'perl', 'css': 'text-dark'},
    {'name': 'python', 'css': 'text-danger fw-bold fs-5'},
    {'name': 'TechnoPark', 'css': 'text-dark'},
    {'name': 'MySQL', 'css': 'text-danger fw-bold fs-5'},
    {'name': 'django', 'css': 'text-success fw-bold'},
    {'name': 'Mail.Ru', 'css': 'text-dark'},
    {'name': 'Voloshin', 'css': 'text-dark'},
    {'name': 'Firefox', 'css': 'text-warning'},
  ]

  best_members = [
    'Mr. Freeman',
    'Dr. House',
    'Bender',
    'Queen Victoria',
    'V. Pupkin'
  ]

  return {
    'popular_tags': popular_tags,
    'best_members': best_members
  }
